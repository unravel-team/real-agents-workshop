import dspy

def validate_answer(example, prediction, trace=None):
    """Check if the answer matches the ground truth."""
    # Simple exact match for demo purposes
    return prediction.answer.lower() == example.answer.lower()

def run_evals(agent, dataset):
    """Run evaluation on a dataset."""
    evaluator = dspy.Evaluate(devset=dataset, metric=validate_answer, num_threads=4, display_progress=True)
    score = evaluator(agent)
    return score
