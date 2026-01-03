# Module 3: Observability & Evals

**Goal**: Stop guessing. Start measuring.

An agent without evals is a toy. In this module, we introduce:
1.  **Tracing**: Seeing exactly what the LLM thought and called.
2.  **Dataset Creation**: How to curate "golden" examples.
3.  **Metrics**: Automated ways to check if the agent succeeded.

## Code Structure

- `trace_utils.py`: Sets up Langfuse for visualization.
- `evaluate.py`: Defines the custom metric logic.

## Exercises

Open `notebook.ipynb`.

1.  **Instrument the Agent**: Add tracing to see the intermediate `Search` calls.
2.  **Create a Dataset**: define 5 hard examples.
3.  **Run the Benchmark**: Use `dspy.Evaluate` to get a % score.
