import dspy

# Small training set for few-shot optimization
train_data = [
    dspy.Example(question="What is the capital of France?", answer="Paris").with_inputs("question"),
    dspy.Example(question="Who wrote Hamlet?", answer="William Shakespeare").with_inputs("question"),
    dspy.Example(question="What is the speed of light?", answer="299,792,458 m/s").with_inputs("question"),
]

# Validation set for checking generalization
dev_data = [
    dspy.Example(question="What is the capital of Germany?", answer="Berlin").with_inputs("question"),
    dspy.Example(question="Who wrote Macbeth?", answer="William Shakespeare").with_inputs("question"),
]
