"""Side-by-side HTML comparison of expected vs generated eval results."""

from __future__ import annotations

import html
from io import StringIO

import pandas as pd
from IPython.display import HTML, display


def _score_color(score: float) -> str:
    if score >= 0.8:
        return "#22c55e"  # green
    if score >= 0.5:
        return "#eab308"  # yellow
    return "#ef4444"  # red


def _score_badge(label: str, score: float | None, reasoning: str | None) -> str:
    if score is None:
        return ""
    color = _score_color(score)
    badge = (
        f'<div style="display:block;margin-right:16px;">'
        f'<span style="background:{color};color:#fff;padding:4px 10px;'
        f'border-radius:4px;font-weight:600;font-size:14px;">'
        f"{label}: {score:.2f}</span>"
    )
    if reasoning:
        badge += (
            f'<div style="color:#000;font-size:12px;margin-top:4px;">'
            f"{html.escape(reasoning)}</div>"
        )
    badge += "</div>"
    return badge


def _sql_panel(title: str, sql: str | None) -> str:
    content = html.escape(sql) if sql else "<em>No SQL</em>"
    return (
        f'<div style="flex:1;min-width:0;">'
        f'<h4 style="margin:0 0 8px 0;font-size:14px;color:#000;">{title}</h4>'
        f'<pre style="background:#fff;padding:12px;border-radius:6px;color:#000;'
        f"overflow-x:auto;font-size:12px;line-height:1.5;margin:0;"
        f'border:1px solid #ddd;white-space:pre-wrap;word-break:break-word;">{content}</pre>'
        f"</div>"
    )


def _df_panel(title: str, csv_str: str | None, max_rows: int = 50) -> str:
    if not csv_str:
        inner = '<em style="color:#999;">No output</em>'
    else:
        try:
            df = pd.read_csv(StringIO(csv_str))
            inner = df.head(max_rows).to_html(
                index=False,
                classes="compare-table",
                border=0,
            )
        except Exception:
            inner = f'<pre style="font-size:12px;">{html.escape(csv_str[:2000])}</pre>'
    return (
        f'<div style="flex:1;min-width:0;overflow-x:auto;">'
        f'<h4 style="margin:0 0 8px 0;font-size:14px;color:#000;">{title}</h4>'
        f"{inner}</div>"
    )


TABLE_CSS = """
<style>
.compare-table { font-size: 12px; border-collapse: collapse; width: 100%;
                 color: #000; background: #fff; }
.compare-table th { background: #f0f0f0; color: #000; padding: 6px 8px; text-align: left;
                     border-bottom: 2px solid #ddd; white-space: nowrap; }
.compare-table td { padding: 4px 8px; border-bottom: 1px solid #eee; color: #000; }
</style>
"""


def display_comparison(
    question: str,
    reference_sql: str,
    agent_sql: str | None,
    expected_csv: str,
    agent_csv: str | None,
    answer_quality_score: float | None = None,
    answer_quality_reasoning: str | None = None,
) -> None:
    """Render a side-by-side HTML comparison of expected vs generated results."""
    parts: list[str] = [TABLE_CSS]

    # Container
    parts.append(
        '<div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:20px;'
        'margin-bottom:24px;font-family:system-ui,sans-serif;color:#000;">'
    )

    # Header
    parts.append(
        f'<div style="font-size:15px;font-weight:600;margin-bottom:12px;color:#000;">'
        f"{html.escape(question)}</div>"
    )

    # Judge badge
    badge = _score_badge("Answer Quality", answer_quality_score, answer_quality_reasoning)
    if badge:
        parts.append(f'<div style="margin-bottom:16px;">{badge}</div>')

    # SQL comparison
    parts.append('<div style="display:flex;gap:16px;margin-bottom:20px;">')
    parts.append(_sql_panel("Reference SQL", reference_sql))
    parts.append(_sql_panel("Agent SQL", agent_sql))
    parts.append("</div>")

    # Output comparison
    parts.append('<div style="display:flex;gap:16px;">')
    parts.append(_df_panel("Expected Output", expected_csv))
    parts.append(_df_panel("Agent Output", agent_csv))
    parts.append("</div>")

    # Close container
    parts.append("</div>")

    display(HTML("\n".join(parts)))
