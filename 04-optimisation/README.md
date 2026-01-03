# Module 4: Optimisation

**Goal**: Systematically improve the agent, instead of guessing prompts.

In this module, we use DSPy optimizers (Teleprompters) to "compile" our agent.
This mechanically improves the instructions and few-shot examples included in the prompt.

## Code Structure

- `dataset.py`: A small set of inputs/outputs to train on.
- `optimize.py`: Script to run the `BootstrapFewShot` optimizer.

## Exercises

Open `notebook.ipynb`.

1.  **Baseline**: Measure the 0-shot performance of our agent.
2.  **Compile**: Run `BootstrapFewShot` to generate an optimized version.
3.  **Inspect**: Look at the "compiled" prompts to see what the optimizer learned.
4.  **Verify**: Re-run the benchmark to confirm the score improved.
