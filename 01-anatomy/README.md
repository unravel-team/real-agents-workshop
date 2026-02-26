# Module 1: Anatomy of a Production Agent

**Goal**: Understand the building blocks of an AI agent using DSPy — from simple LLM calls to tool-using agents.

In this module, we will progressively build up agent capabilities:

1. **Signatures**: Declarative input/output specs that tell the LM *what* to do, not *how*.
2. **Modules (Predict)**: The base predictor module that interacts with the LLM for a given task.
3. **Chain of Thought**: Prompting the LLM to reason step-by-step before answering.
4. **ReAct**: A tool-using agent that combines reasoning with function calls.

## Exercises

Open `intro.ipynb` to follow along.

1. **Signatures** — Define inline (`"question -> answer"`) and class-based signatures for structured tasks like sentiment classification.
2. **Order Issue Triager** — Build an agent that triages food delivery order issues into categories: `no_issue`, `late_order`, `severely_late_order`, `fulfillment_issue`, `consumer_issue`.
3. **Chain of Thought** — Upgrade the triager with step-by-step reasoning for better accuracy on edge cases.
4. **ReAct with Tools** — Give the agent a `normalize_delivery_time` tool to compute delivery delays before classifying.
