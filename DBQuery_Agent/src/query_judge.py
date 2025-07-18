from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage,BaseMessage,HumanMessage
from state import *
from utils import *
from pydantic import BaseModel, Field
from agentops.sdk.decorators import agent,operation
import asyncio
import chainlit as cl

class judgeReflection(BaseModel):
    coherence_rating:str = Field(...,description="Respond Excellent/ Good/ Poor based on whether the output is logically structured,clear or not")
    coherence_explained:str = Field(...,description="Short Explanation of the coherence rating")
    relevance_rating:str = Field(...,description="Respond Excellent/ Good/ Poor based on whether the output directly address the user's question")
    relevance_explained:str = Field(...,description="Short Explanation of the relevance rating")
    correctness_rating:str = Field(...,description="Respond Excellent/ Good/ Poor based on whether the output is factually accurate or not based on the SQL result")
    correctness_explained:str = Field(...,description="Short Explanation of the correctness rating")
    final_verdict:str = Field(...,description='Respond with "ACCEPT" if all three are Good or Excellent\
                              or else respond "RETRY" if any of them is Poor') 
    node_retry:str = Field(...,description='If the final verdict is *RETRY*, then which node to rerun,\
                                response should be *SQLGenerator* or *ToolNode*. If final verdict is *ACCEPT* response should be *None*')

@agent(name="LLM_judge_workflow_reflection")
class LLM_judge:

    @staticmethod    
    @cl.step(name="LLM judge")
    @operation(name="judge_reflection_operation")
    def judge_reflect(state:AgentState):

        #state['full_reflection_iter'] = 0

        print("\nLLM judge: Reflecting on the entire flow of actions")
        REFLECTION_JUDGE_PROMPT = """
                You are an intelligent judge that evaluates whether the generated output answers the user's question accurately.
                Review the following, also providing database schema and database description.

                User Query:
                {user_query}

                Generated SQL:
                {sql_query}

                SQL Output:
                {sql_result}

                Tool Used: 
                {tool_name}

                Tool Description:
                {tool_description}
                
                Database Schema:
                {schema}

                Database description:
                The Chinook database is a sample SQL database that simulates a digital music store.\
                It contains tables for artists, albums, tracks, customers, invoices, and employees

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

                If RETRY, suggest which node has to be retried: e.g., SQLGenerator, ToolNode,\
                If ACCEPT, node retry should be responded as None
    """
        # if "full_reflection" not in state or state["full_reflection"] is None:
        #     state["full_reflection"] = []
        #     state['full_reflection_iter'] = 0

        schema_desc = schema_knowledge
        async def judge_step_logic():
            async with cl.Step(name="🔍 Thinking, Acting and Tool executors", type="run"):
                judge_prompt_template = ChatPromptTemplate.from_template(REFLECTION_JUDGE_PROMPT)
                llm_judge_model = llm_judge.with_structured_output(judgeReflection)
                judge_chain = judge_prompt_template | llm_judge_model
                user_query = state['question'].content
                sql_query = state['sql_query']
                sql_out_result = state['sql_result']
                tool_name = state['next_tool_selection']
                tool_desc = tool_descriptors[tool_name]
                response = judge_chain.invoke({
                        "user_query":user_query,"sql_query":sql_query,"sql_result":sql_out_result,"tool_name":tool_name,\
                        "tool_description":tool_desc,"schema":schema_desc
                })
                return response
        response = asyncio.run(judge_step_logic())
        #print(dict(response))
        
        state["full_reflection"].append(dict(response))
        print("\n State after full reflection:",state)
        print("LLM Judge action completed")
        return state

if __name__ == "__main__":
    state_test = {'question': HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}), 'messages': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}), AIMessage(content='Yes', additional_kwargs={'pydantic_model': 'ClassifyQuestion'}, response_metadata={}), AIMessage(content='SELECT Album.Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"', additional_kwargs={'pydantic_model': 'SQLOutput'}, response_metadata={})], 'question_history': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={})],\
                'on_topic_classifier': 'Yes', \
                'sql_query': 'SELECT Album.Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"',\
                 'sql_query_columns': ['AlbumTitle'],\
                 'next_tool_selection': 'text_listing_tool',
                'sql_query_history': ['SELECT Album.Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"'],\
                 'sql_result_history': ['["Garage Inc. (Disc 1)", "Black Album", "Garage Inc. (Disc 2)", "Kill \'Em All", "Load", "Master Of Puppets", "ReLoad", "Ride The Lightning", "St. Anger", "...And Justice For All"]'],\
                'sql_result': '["Garage Inc. (Disc 1)", "Black Album", "Garage Inc. (Disc 2)", "Kill \'Em All", "Load", "Master Of Puppets", "ReLoad", "Ride The Lightning", "St. Anger", "...And Justice For All"]'}
    state = LLM_judge.judge_reflect(state_test)
    print(state)