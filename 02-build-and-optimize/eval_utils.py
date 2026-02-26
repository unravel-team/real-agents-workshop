"""Eval runner for text2sql agents."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

os.environ["TQDM_DISABLE"] = "1"

import dspy


# --- Trajectory helpers ---


def extract_sqls_from_trajectory(trajectory: dict) -> list[str]:
    """Extract all SQL queries from a DSPy ReAct trajectory."""
    sqls = []
    i = 0
    while f"tool_name_{i}" in trajectory:
        if trajectory[f"tool_name_{i}"] == "execute_sql":
            args = trajectory[f"tool_args_{i}"]
            if isinstance(args, str):
                args = json.loads(args)
            sql = args.get("sql", "")
            if sql:
                sqls.append(sql)
        i += 1
    return sqls


def get_last_analytical_sql(trajectory: dict) -> str | None:
    """Get the last non-exploratory SQL from the trajectory."""
    sqls = extract_sqls_from_trajectory(trajectory)
    for sql in reversed(sqls):
        upper = sql.strip().upper()
        if not upper.startswith(("SHOW", "DESCRIBE")):
            return sql
    return sqls[-1] if sqls else None


# --- DSPy Judge Signature ---


class JudgeSignature(dspy.Signature):
    """Rate how well the agent answered a data analysis question.

    Evaluate both the SQL approach and the output data holistically.

    For the SQL query, ignore superficial differences such as:
    - Aliases and formatting
    - JOIN syntax variations
    - Column order
    - Equivalent date functions
    - Additional ORDER BY/LIMIT clauses

    For the output data, ignore superficial differences such as:
    - Different column names for the same data (e.g. "store" vs "store_name")
    - Different row ordering
    - Minor rounding differences (e.g. 14.7 vs 14.71)
    - Extra columns that don't change the core answer
    - Different date/time formatting (e.g. "2025-11" vs "2025-11-01")

    Consider the answer incorrect only if the core logic or data differs:
    - Wrong GROUP BY, aggregations, filters, or JOINs
    - Significantly different row counts or wrong values
    - Missing key columns that the question asked for
    """

    question: str = dspy.InputField(desc="The natural language question")
    reference_sql: str = dspy.InputField(desc="The ground truth SQL query")
    agent_sql: str = dspy.InputField(desc="The agent-generated SQL query")
    expected_csv: str = dspy.InputField(desc="The expected output data (CSV)")
    agent_csv: str = dspy.InputField(desc="The agent-generated output data (CSV)")
    score: float = dspy.OutputField(desc="Score between 0 and 1")
    reasoning: str = dspy.OutputField(desc="Brief explanation of the score")


_judge = dspy.Predict(JudgeSignature)


# --- Judge runner ---


def answer_quality(
    agent_sql: str, reference_sql: str, expected_csv: str, question: str, conn
) -> dict:
    """Execute agent SQL and use an LLM judge to score the result."""
    if not agent_sql:
        return {
            "score": 0.0,
            "reasoning": "No analytical SQL found",
            "agent_csv": None,
        }

    try:
        result_df = conn.execute(agent_sql).fetchdf()
        agent_csv_str = result_df.to_csv(index=False)
    except Exception as e:
        return {
            "score": 0.0,
            "reasoning": f"SQL execution error: {e}",
            "agent_csv": None,
        }

    agent_csv_full = agent_csv_str

    # Truncate copies for the judge prompt
    agent_lines = agent_csv_str.strip().split("\n")
    if len(agent_lines) > 51:
        agent_csv_str = (
            "\n".join(agent_lines[:51]) + f"\n... ({len(agent_lines) - 1} total rows)"
        )

    expected_lines = expected_csv.strip().split("\n")
    if len(expected_lines) > 51:
        expected_csv = (
            "\n".join(expected_lines[:51])
            + f"\n... ({len(expected_lines) - 1} total rows)"
        )

    try:
        result = _judge(
            question=question,
            reference_sql=reference_sql,
            agent_sql=agent_sql,
            expected_csv=expected_csv,
            agent_csv=agent_csv_str,
        )
        return {
            "score": float(result.score),
            "reasoning": result.reasoning,
            "agent_csv": agent_csv_full,
        }
    except Exception as e:
        return {
            "score": 0.0,
            "reasoning": f"Judge error: {e}",
            "agent_csv": agent_csv_full,
        }


# --- Automatic metrics ---


def _sql_validity(trajectory: dict) -> float:
    """Fraction of SQL tool calls that did NOT return an error."""
    errors = total = 0
    i = 0
    while f"observation_{i}" in trajectory:
        if trajectory.get(f"tool_name_{i}") == "execute_sql":
            total += 1
            if trajectory[f"observation_{i}"].startswith("SQL Error:"):
                errors += 1
        i += 1
    return (total - errors) / total if total else 1.0


def _tool_efficiency(trajectory: dict) -> float:
    """Score based on number of tool calls. Fewer is better."""
    i = 0
    while f"observation_{i}" in trajectory:
        i += 1
    if i <= 4:
        return 1.0
    if i <= 7:
        return 0.5
    return 0.25


def _error_recovery(trajectory: dict, answer: str) -> float:
    """Did the agent self-correct after SQL errors?"""
    errors = 0
    i = 0
    while f"observation_{i}" in trajectory:
        if trajectory.get(f"tool_name_{i}") == "execute_sql":
            if trajectory[f"observation_{i}"].startswith("SQL Error:"):
                errors += 1
        i += 1
    if errors == 0:
        return 1.0
    if answer and answer != "(No response)":
        return 0.75
    return 0.0


# --- Public API ---


def run_single_eval(agent, example: dict, conn, **agent_kwargs) -> dict:
    """Run a single eval example through the agent and score it.

    Returns a result dict with all scores, agent SQL, agent CSV, etc.
    Extra **agent_kwargs are forwarded to the agent call (e.g. db_context).
    """
    t0 = time.time()

    try:
        result = agent(question=example["question"], **agent_kwargs)
        answer = result.answer
        trajectory = result.trajectory
    except Exception as e:
        return {
            "id": example["id"],
            "difficulty": example["difficulty"],
            "answer_quality_score": 0.0,
            "answer_quality_reasoning": f"Agent error: {e}",
            "sql_validity": 0.0,
            "tool_efficiency": 0.0,
            "error_recovery": 0.0,
            "agent_sql": None,
            "agent_csv": None,
            "answer": str(e)[:200],
            "elapsed_secs": round(time.time() - t0, 1),
        }

    agent_sql = get_last_analytical_sql(trajectory)
    elapsed = round(time.time() - t0, 1)

    # Impossible questions: score 1.0 only if the agent correctly refused (no SQL)
    if example.get("impossible") and not agent_sql:
        return {
            "id": example["id"],
            "difficulty": example["difficulty"],
            "answer_quality_score": 1.0,
            "answer_quality_reasoning": "Impossible question — agent correctly refused",
            "sql_validity": 1.0,
            "tool_efficiency": 1.0,
            "error_recovery": 1.0,
            "agent_sql": None,
            "agent_csv": None,
            "answer": answer[:200],
            "elapsed_secs": elapsed,
        }

    # LLM Judge (combined SQL + output evaluation)
    judge_result = answer_quality(
        agent_sql, example["reference_sql"], example["expected_answer"],
        example["question"], conn
    )

    # Automatic metrics
    sv = _sql_validity(trajectory)
    te = _tool_efficiency(trajectory)
    er = _error_recovery(trajectory, answer)

    return {
        "id": example["id"],
        "difficulty": example["difficulty"],
        "answer_quality_score": judge_result["score"],
        "answer_quality_reasoning": judge_result["reasoning"],
        "sql_validity": sv,
        "tool_efficiency": te,
        "error_recovery": er,
        "agent_sql": agent_sql,
        "agent_csv": judge_result.get("agent_csv"),
        "answer": answer[:200],
        "elapsed_secs": elapsed,
    }


def run_eval(
    agent,
    dataset: list[dict],
    conn,
    agent_name: str = "agent",
    **agent_kwargs,
) -> list[dict]:
    """Run eval examples through the agent, score with judges + metrics.

    Prints a results table and returns the list of per-example result dicts.
    Extra **agent_kwargs are forwarded to each agent call (e.g. db_context).
    """
    eval_results: list[dict] = []

    print(f"Running eval on {len(dataset)} examples with {agent_name}\n")
    print(
        f"{'#':<3} {'ID':<35} {'Difficulty':<12} {'Efficiency':<12} {'SQLValid':<10} {'Recovery':<10} {'Answer Quality':<10}"
    )
    print("-" * 100)

    for i, example in enumerate(dataset):
        r = run_single_eval(agent, example, conn, **agent_kwargs)
        eval_results.append(r)

        print(
            f"{i + 1:<3} {r['id']:<35} {r['difficulty']:<12} "
            f"{r['tool_efficiency']:<12.2f} {r['sql_validity']:<10.2f} "
            f"{r['error_recovery']:<10.2f} {r['answer_quality_score']:<10.2f} ({r['elapsed_secs']}s)"
        )

    print("-" * 100)

    # Averages
    n = len(eval_results)
    avg_judge = sum(r["answer_quality_score"] for r in eval_results) / n
    avg_sv = sum(r["sql_validity"] for r in eval_results) / n
    avg_te = sum(r["tool_efficiency"] for r in eval_results) / n
    avg_er = sum(r["error_recovery"] for r in eval_results) / n
    total_time = sum(r["elapsed_secs"] for r in eval_results)

    print(
        f"{'AVG':<3} {'':<35} {'':<12} {avg_te:<12.2f} {avg_sv:<10.2f} "
        f"{avg_er:<10.2f} {avg_judge:<10.2f} ({total_time:.0f}s)"
    )

    return eval_results


def save_eval(
    eval_id: str,
    question: str,
    sql: str,
    conn,
    difficulty: str = "medium",
    expected_tables: list[str] | None = None,
    base_dir: str | Path = ".",
) -> dict:
    """Save a new eval example: run SQL, write CSV + SQL files, return dataset entry.

    Args:
        eval_id: Identifier like "17_my_query" (used as filename prefix).
        question: The natural language question.
        sql: The reference SQL query.
        conn: DuckDB connection to execute the SQL.
        difficulty: One of "easy", "medium", "hard", "impossible".
        expected_tables: List of tables used (optional, for documentation).
        base_dir: Directory containing eval_answer_csvs/ and eval_answer_sqls/.

    Returns:
        A dataset entry dict compatible with DATASET format.
    """
    base = Path(base_dir)
    csv_dir = base / "eval_answer_csvs"
    sql_dir = base / "eval_answer_sqls"
    csv_dir.mkdir(exist_ok=True)
    sql_dir.mkdir(exist_ok=True)

    # Write SQL file
    sql_path = sql_dir / f"{eval_id}.sql"
    sql_path.write_text(sql)

    # Execute SQL and write CSV
    result_df = conn.execute(sql).fetchdf()
    csv_path = csv_dir / f"{eval_id}.csv"
    result_df.to_csv(csv_path, index=False)

    print(f"Saved {eval_id}:")
    print(f"  SQL → {sql_path}")
    print(f"  CSV → {csv_path} ({len(result_df)} rows)")

    return {
        "id": eval_id,
        "question": question,
        "expected_tables": expected_tables or [],
        "expected_answer": csv_path.read_text(),
        "reference_sql": sql,
        "difficulty": difficulty,
        "impossible": difficulty == "impossible",
    }
