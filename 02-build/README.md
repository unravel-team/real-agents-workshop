# Module 2: Build the Agent in DSPy

**Goal**: Move from brittle strings to modular, typed code.

In this module, we replace our "while True" loop with DSPy modules.
Why DSPy?
1.  **Signatures**: Abstract away specific prompts (e.g., "You are a helpful assistant...").
2.  **Modules**: Compose prompts like Pytorch layers (`ChainOfThought`, `ReAct`, etc.).

## Code Structure

- `signatures.py`: Defines the inputs/outputs (the "API" of our AI tasks).
- `agent.py`: Wire up logic (`Goal -> Search -> Answer`).

## Exercises

Open `notebook.ipynb`.

1.  **Define Signatures**: Write `BasicQA` and `SearchQuery` signatures.
2.  **Build the Module**: Subclass `dspy.Module` to define the control flow.
3.  **Run It**: Connect to LLM and test the module manually.
