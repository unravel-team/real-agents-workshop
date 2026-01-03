# Module 5: Shipping the Improvement Loop

**Goal**: Make quality control automatic.

If evals don't run automatically, they stop running.
In this module, we set up a CI/CD pipeline that blocks regressions.

## Code Structure

- `.github/workflows/agent-eval.yml`: A Github Action that runs our evals on every PR.

## Exercises

1.  **Regressions**: Deliberately break the agent code.
2.  **CI/CD**: Push the change and watch GitHub Actions fail.
3.  **Versioning**: Discuss strategies for versioning prompts/programs (e.g., MLflow, git tags).
