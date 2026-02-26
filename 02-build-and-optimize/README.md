# Module 2: Build and Optimize

**Goal**: Build a Text-to-SQL ReAct agent with DSPy, evaluate it with structured metrics, and optimize it using automated prompt tuning.

In this module, we will build and iteratively improve a data analysis agent:

1. **Text-to-SQL Agent**: A ReAct agent that translates natural language questions into SQL queries against a DuckDB database.
2. **Marker Agent**: A secondary LLM that audits the agent's SQL and answer for correctness, gaps, and confidence.
3. **Evals**: Structured metrics — tool efficiency, SQL validity, error recovery, and LLM-judged answer quality.
4. **Optimization**: Use DSPy's GEPA optimizer to automatically improve the agent's prompts and performance.

## Exercises

Open `build-and-optimize.ipynb` to follow along.

1. **Connect to DuckDB** — Load the quick-commerce dataset (`qc_pune.duckdb`) and explore the schema (consumers, itemized_orders, product_catalogue, stores).
2. **Build Agent V1** — Create a `dspy.ReAct` agent with an `execute_sql` tool that discovers tables, writes SQL, and answers questions.
3. **Marker Agent** — Use a `ChainOfThought` module to explain what the SQL does, check if it answers the question, and flag gaps.
4. **Define Metrics** — Implement tool efficiency (fewer calls = better), SQL validity (error-free queries), error recovery (self-correction), and answer quality (LLM judge comparing agent output to reference).
5. **Run Evals** — Score the agent across easy, medium, hard, and impossible questions to identify failure patterns.
6. **Add Your Own Eval** — Use `save_eval` to create custom eval examples from a question + SQL query.
7. **Improve with DB Context (Agent V2)** — Pass full schema documentation upfront so the agent skips discovery and goes straight to analytical queries.
8. **Optimize with GEPA** — Use DSPy's Genetic-Pareto optimizer to automatically tune the agent's prompts using reflective feedback from execution traces.
