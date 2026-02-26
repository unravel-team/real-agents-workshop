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

## Workshop Outline (~2 h 15 min)

1.  **[Anatomy of a Production Agent](./01-anatomy/) (30 min)**
    Agent loop, DSPy signatures & modules, Predict, Chain of Thought, ReAct with tool use.

2.  **[Build & Optimise a Text-to-SQL Agent](./02-build-and-optimize/)**

    a. **Build** (30 min) — DuckDB + `execute_sql` tool, ReAct agent, marker agent.

    b. **Evaluate** (45 min) — 4 metrics (tool efficiency, SQL validity, error recovery, answer quality), run evals, add custom evals, debugging.

    c. **Optimise** (30 min) — Agent V2 (DB context injection), GEPA optimiser, compare results.

## Repo Setup

- [Python **3.11+**](https://www.python.org/downloads/)
- [Git](https://git-scm.com/install/)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — fast Python package manager
- [DuckDB CLI](https://duckdb.org/install/?environment=cli) — local analytical database
- **LLM API key** (one of): [OpenRouter](https://openrouter.ai/settings/keys) (recommended), OpenAI, Anthropic, or Gemini
- **Langfuse** (optional, for observability): [Cloud setup](https://langfuse.com/docs/observability/get-started) or [Local Docker](https://langfuse.com/docs/deployment/local)

### Validate Your Setup

After cloning, verify all prerequisites with a single command:

**macOS / Linux:**
```bash
bash validate.sh
```

**Windows:**
```cmd
validate.bat
```

This checks for Git, Python 3.11+, uv, DuckDB, required API keys, and then installs dependencies via `uv sync`.

### Download Data

Once setup is validated, download the workshop dataset:

```bash
uv run download_data.py
```
