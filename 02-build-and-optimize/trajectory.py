"""Render a DSPy ReAct trajectory as a human-readable Markdown file."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _fmt_tool_args(args: dict | str) -> str:
    """Format tool arguments for display."""
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            return args

    parts = []
    for key, value in args.items():
        if isinstance(value, str) and "\n" in value:
            parts.append(f"**{key}**:\n```sql\n{value}\n```")
        elif isinstance(value, str) and len(value) > 80:
            parts.append(f"**{key}**:\n```\n{value}\n```")
        else:
            parts.append(f"**{key}**: `{value}`")
    return "\n".join(parts)


def _truncate(text: str, max_lines: int = 30) -> str:
    """Truncate long text output, keeping head and tail."""
    lines = text.split("\n")
    if len(lines) <= max_lines:
        return text
    head = "\n".join(lines[:max_lines])
    return f"{head}\n\n*... ({len(lines) - max_lines} more lines)*"


def save_trajectory(
    trajectory: dict,
    lm_usage: dict | None = None,
    *,
    name: str = "trajectory",
    output_dir: str | Path = "trajectories",
) -> Path:
    """Write a Markdown file summarising a DSPy ReAct trajectory.

    Parameters
    ----------
    trajectory : dict
        The ``result.trajectory`` dict from a ``dspy.ReAct`` call.
    lm_usage : dict | None
        Token usage dict from ``result.get_lm_usage()``.
    name : str
        Base name for the output file (timestamp is prepended automatically).
    output_dir : str | Path
        Directory to write the ``.md`` file into (created if missing).

    Returns
    -------
    Path
        Path to the generated Markdown file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Count iterations
    n_iters = 0
    while f"thought_{n_iters}" in trajectory:
        n_iters += 1

    # Build markdown
    lines: list[str] = []

    # Header
    lines.append("# Agent Trajectory")
    lines.append("")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if lm_usage:
        model_name = next(iter(lm_usage), None)
        if model_name:
            lines.append(f"**Model**: `{model_name}`  ")
    lines.append(f"**Iterations**: {n_iters}  ")
    lines.append(f"**Generated**: {timestamp}")
    lines.append("")

    # Steps
    lines.append("## Trajectory")
    lines.append("")

    for i in range(n_iters):
        thought = trajectory.get(f"thought_{i}", "")
        tool_name = trajectory.get(f"tool_name_{i}", "")
        tool_args = trajectory.get(f"tool_args_{i}", {})
        observation = trajectory.get(f"observation_{i}", "")

        lines.append(f"### Step {i + 1}")
        lines.append("")

        # Thought
        lines.append(f"**Thought**: {thought}")
        lines.append("")

        # Tool call
        if tool_name == "finish":
            lines.append("**Tool**: `finish`")
        else:
            lines.append(f"**Tool**: `{tool_name}`")
            lines.append("")
            lines.append(_fmt_tool_args(tool_args))

        lines.append("")

        # Observation
        if tool_name != "finish" and observation:
            lines.append("**Observation**:")
            lines.append("")
            lines.append(f"```\n{_truncate(observation)}\n```")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Usage stats
    if lm_usage:
        lines.append("## Usage")
        lines.append("")
        for model_name, stats in lm_usage.items():
            lines.append(f"**{model_name}**")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")

            prompt_tokens = stats.get("prompt_tokens", 0)
            completion_tokens = stats.get("completion_tokens", 0)
            cached_tokens = (stats.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
            non_cached_prompt = prompt_tokens - cached_tokens
            non_cached_total = non_cached_prompt + completion_tokens

            lines.append(f"| Prompt tokens | {prompt_tokens} |")
            lines.append(f"| Cached tokens | {cached_tokens} |")
            lines.append(f"| Non-cached prompt tokens | {non_cached_prompt} |")
            lines.append(f"| Completion tokens | {completion_tokens} |")
            lines.append(f"| Non-cached total | {non_cached_total} |")

            # Cost for non-cached tokens only (pro-rate prompt cost, full completion cost)
            cost_details = stats.get("cost_details") or {}
            prompt_cost = cost_details.get("upstream_inference_prompt_cost")
            completion_cost = cost_details.get("upstream_inference_completions_cost")
            if prompt_cost is not None and completion_cost is not None and prompt_tokens > 0:
                non_cached_prompt_cost = prompt_cost * (non_cached_prompt / prompt_tokens)
                non_cached_cost = non_cached_prompt_cost + completion_cost
                lines.append(f"| Cost (non-cached) | ${non_cached_cost:.6f} |")
            elif stats.get("cost") is not None:
                lines.append(f"| Cost (total) | ${stats['cost']:.6f} |")

            lines.append("")

    # Write file
    filename = f"{name}.md"
    filepath = output_dir / filename
    filepath.write_text("\n".join(lines))

    return filepath
