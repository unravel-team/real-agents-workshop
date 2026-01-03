import dspy

class BasicQA(dspy.Signature):
    """Answer questions with short, factual responses."""
    
    question = dspy.InputField()
    context = dspy.InputField(desc="Relevant facts found by search")
    answer = dspy.OutputField(desc="A concise 1-sentence answer")

class SearchQuery(dspy.Signature):
    """Generate a search query based on the user question."""
    
    question = dspy.InputField()
    query = dspy.OutputField()
