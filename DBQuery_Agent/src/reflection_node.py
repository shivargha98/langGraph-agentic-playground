from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage,BaseMessage,HumanMessage
from state import *
from utils import *
from pydantic import BaseModel, Field
import asyncio
from agentops.sdk.decorators import operation,agent


with open("D:\langGraph-agentic-playground\DBQuery_Agent\schema_file.txt","r") as f:
    schema_desc = f.read()


class Reflection(BaseModel):

    revised_sql_query:str = Field(...,description='Revised SQL qeury or the original query if there is no optimisation required.')
    revision_flag:str = Field(...,description="Flag for revision, output -> 'Yes' if a revision was made, 'No' if revisoon was not made.")
    query_reflection:str =  Field(...,description="Reflection on why the changes were made to the original user query or why the original query is optimal.")

@agent(name="SQL_query_reflection")
class SQL_query_reflect:

    @staticmethod
    @cl.step(type="Reflection")
    @operation(name="Query_relfection")
    def reflect(state:AgentState):

        print("\nReflecting on the SQL Query, Can it be optimised?")

        async def reflect_step_logic():
            async with cl.Step(name="🔍 Reflecting over SQL Execution,Generation", type="run"):

                prompt = '''
                You are an expert SQL analyst.
                Your job is to review a generated SQL query based on the user question,schema of the database,description of the database\
                    and improve it if necessary. Evaluate the query for correctness, efficiency, and completeness.
                ---
                User Question:
                {user_question}

                Database Schema:
                {schema}

                Database description:
                The Chinook database is a sample SQL database that simulates a digital music store.\
                It contains tables for artists, albums, tracks, customers, invoices, and employees

                Generated SQL Query:
                {sql_query}
                ---

                Reflect on the following:
                1. Is the SQL query logically correct and aligned with the user intent?
                2. Is the SQL query efficient — are there unnecessary joins, wildcards (SELECT *), or filters that could be improved?
                3. Can the query be optimized further or rewritten more concisely?

                If the query is already optimal, return it as-is. Otherwise, revise the SQL query to a better version.
                Respond with **the final SQL query**.
                Also, if there was a revision made, respond with *Yes* and if there is no revision respond wih *No* to the revision flag parameter.
                Also,summarise the reflection as to why the change was made or to why the query is correct, keep it short and precise.
                '''
                
                #schema_desc = schema_knowledge
                prompt_template = ChatPromptTemplate.from_template(prompt)
                qwen_model = llm_qwen_coder.with_structured_output(Reflection)
                revisor_chain = prompt_template | qwen_model
                user_query = state['question'].content
                sql_query = state['sql_query']
                response = revisor_chain.invoke({'user_question':user_query,'schema':schema_desc,'sql_query': sql_query})
                return response
        
        response = asyncio.run(reflect_step_logic())
        #print(response)
        if response.revision_flag.lower().strip() == "no":
            pass
        else:
            state['sql_query'] = response.revised_sql_query.strip()
            state['sql_query_history'].append(response.revised_sql_query.strip())

        state['sql_query_reflection_history'].append(dict(response))

        print("Reflecting Completed")
        #print("\n state after reflection:",state)
        return state
        


if __name__ == "__main__":
    state = {'messages': [HumanMessage(content='Show monthly revenue from invoice sales', additional_kwargs={}, response_metadata={}),
    AIMessage(content="SELECT strftime('%Y-%m', InvoiceDate) AS month, SUM(Total) AS revenue FROM Invoice GROUP BY month ORDER BY month;", additional_kwargs={}, response_metadata={})],
    'sql_result': '',
    'question': HumanMessage(content='Show monthly revenue from invoice sales', additional_kwargs={}, response_metadata={}),
    'sql_query': "SELECT strftime('%Y-%m', InvoiceDate) AS month, SUM(Total) AS revenue FROM Invoice GROUP BY month ORDER BY month;",
    'sql_query_columns': ['month', 'revenue'],
    'sql_query_reflection_history':[],
    'next_tool_selection': 'sqlexecutor'}
    SQL_query_reflect.reflect(state)