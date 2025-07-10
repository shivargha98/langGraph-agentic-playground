from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage,BaseMessage,HumanMessage
from state import *
from utils import *
from pydantic import BaseModel, Field

class judgeReflection(BaseModel):
    coherence_rating:str = Field(...,description="Respond Excellent/ Good/ Poor based on whether the output is logically structured,clear or not")
    coherence_explained:str = Field(...,description="Short Explanation of the coherence rating")
    relevance_rating:str = Field(...,description="Respond Excellent/ Good/ Poor based on whether the output directly address the user's question")
    relevance_explained:str = Field(...,description="Short Explanation of the relevance rating")
    correctness_rating:str = Field(...,description="Respond Excellent/ Good/ Poor based on whether the output is factually accurate or not based on the SQL result")
    correctness_explained:str = Field(...,description="Short Explanation of the correctness rating")
    final_verdict:str = Field(...,description='Respond with "ACCEPT" if all three are Good or Excellent\
                              or else respond "RETRY" if any of them is Poor') 
    concerning_node:str = Field(...,description='If the final verdict is *RETRY*, then which node to rerun,\
                                response should be *SQL_generator* or *toolNode*')


def judge_reflect(state:AgentState):

    state['full_reflection_iter'] = 0

    REFLECTION_JUDGE_PROMPT = """
            You are an intelligent judge that evaluates whether the generated output answers the user's question accurately.
            Review the following:

            User Query:
            {user_query}

            Generated SQL:
            {sql_query}

            SQL Output Sample:
            {sql_result}

            Tool Used: 
            {tool_name}


            Evaluate on three criteria:
            1. Coherence — Is the output logically structured and clear?
            2. Relevance — Does the output directly address the user's question?
            3. Correctness — Is the output factually accurate based on the SQL result?

            Respond in this format:

            coherence_rating: [Excellent / Good / Poor] -
            coherence_explained: [Short Explanation of the above coherence rating]
            Relevance: [Excellent / Good / Poor]
            Relevance_explained: [Short Explanation of the above relevance rating]
            Correctness: [Excellent / Good / Poor]
            Correctness_explained: [Short Explanation of the above correctness rating]

            Final Verdict: 
            - "ACCEPT" if all three are Good or Excellent
            - "RETRY" if any of them is Poor

            If RETRY, suggest which node has to be retried: e.g., SQLGenerator, Tools.
"""
