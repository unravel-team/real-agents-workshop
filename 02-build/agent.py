import dspy
from .signatures import BasicQA, SearchQuery

class RagAgent(dspy.Module):
    def __init__(self, retrieval_tool):
        super().__init__()
        self.retrieve = retrieval_tool
        self.generate_query = dspy.ChainOfThought(SearchQuery)
        self.generate_answer = dspy.ChainOfThought(BasicQA)
    
    def forward(self, question):
        # 1. Plan: creating a query
        query_result = self.generate_query(question=question)
        
        # 2. Act: retrieving info
        context = self.retrieve(query_result.query)
        
        # 3. Answer: synthesizing result
        answer_result = self.generate_answer(question=question, context=context)
        
        return dspy.Prediction(answer=answer_result.answer, logic=answer_result.rationale)
