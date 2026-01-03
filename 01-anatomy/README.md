# Module 1: Anatomy of a Production Agent

**Goal**: Move beyond "magical" one-shot prompts to a robust agentic loop.

In this module, we will deconstruct the agent into:
1.  **The Loop**: `Goal -> Plan -> Act -> Observe -> Repeat`
2.  **Tool Contracts**: How to define reliable interfaces for the agent.
3.  **Stop Conditions**: Knowing when to give up or declare success.

## Exercises

Open `notebook.ipynb` to follow along.

1.  **The Naive Loop**: We'll write a simple Python `while` loop that calls an LLM.
2.  **Breaking It**: We'll introduce "real world" noise to see where it breaks.
3.  **Structured Output**: We'll switch from text generation to structured tool calls.
