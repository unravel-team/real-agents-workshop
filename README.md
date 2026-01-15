# Build & Optimise AI Agents That Survive Production

It’s easy to ship a magical agent demo. It’s much harder to ship an agent that works for real users: noisy inputs, partial context, flaky tools, ambiguous goals, and “tiny prompt changes” that break everything.

In this hands-on workshop, we’ll build a small but realistic agent in **Python + DSPy**, then turn it into something you can actually run in production: **structured I/O**, **tool contracts**, **tracing**, **evals**, and **automatic optimisation**.

You’ll leave with a concrete engineering workflow (an “agent improvement loop”) that you can take back to your team:

**instrument → collect failures → convert to evals → optimise → ship via CI**.

> The techniques are framework-agnostic; we’ll use DSPy because it makes optimisation and modularity explicit in code.

## Key Takeaways

- A practical mental model of agents: **goal → plan/act loop → tool calls → ground-truth checks → stop conditions**.
- How to build agents as **maintainable software** (signatures/modules) instead of brittle prompt blobs.
- How to add **observability + evals** so you can debug “why it failed” and measure progress.
- How to use **DSPy optimisers** (few-shot + program/prompt optimisation) to improve quality *systematically*.
- A repeatable **CI workflow** to keep agents improving safely as users and requirements change.

## Target Audience

- **Best suited for:**
    - Software engineers / platform engineers building AI features using LLMs
    - SDETs / QA engineers working on evals and reliability
    - Engineering managers and tech leads who plan to teach scalable agent building and better project planning
- **Level:** Intermediate
- **Prerequisites:**
    - Comfortable with Python (APIs, functions, virtualenv/uv)
    - Basic familiarity with LLMs (prompts, tool calling concepts)
    - Laptop + internet access
    - (Recommended) An API key for any supported LLM provider (OpenAI/Anthropic/etc.)
    - Langfuse (for observability) - [Cloud setup](https://langfuse.com/docs/get-started) or [Local Docker setup](https://langfuse.com/docs/deployment/local)

## Workshop Outline (3 hours)

1.  **[Anatomy of a production agent](./01-anatomy/) (15 min)**
    Agent loop, tool contracts, ground-truth checks, stop conditions, failure modes.

2.  **[Build the agent in DSPy](./02-build/) (60 min)**
    Signatures + modules, tool wiring, structured outputs, error handling.

3.  **[Observability & evals](./03-observability/) (45 min)**
    Tracing, failure buckets, creating an eval set from real-ish cases, measuring baseline.

4.  **[Optimisation](./04-optimisation/) (45 min)**
    Few-shot baselines → DSPy optimiser run → compare metrics + inspect deltas.

5.  **[Shipping the improvement loop](./05-shipping/) (15 min)**
    Minimal CI pattern: run evals on PR, regressions gate merges, version prompts/programs.

## Repo Setup

- Python **3.11+**
- [`uv`](https://docs.astral.sh/uv/)
- Git
