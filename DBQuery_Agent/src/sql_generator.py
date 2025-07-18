from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from pydantic import BaseModel, Field
from state import AgentState
from typing import List
from utils import *
import asyncio
import chainlit as cl
from agentops.sdk.decorators import trace,session,workflow,task,tool,operation,agent


class SQLOutput(BaseModel):
    sql_query:str = Field(...,description="SQL Query generated")
    sql_column_names:List[str] = Field(...,description = "List of column names after data extraction")

@agent(name='SQL_query_generation_agent')
class SQLGen_agent:

    @staticmethod
    @cl.step(type="SQL Generator")
    @operation(name="query_generator_operation")
    def SQLGenerator(state:AgentState):
        #print("inside the SQLGenerator agent; state at the moment:",state)
        #state["sql_query_reflection_history"] = []
        print("\nSQL Query Generation started")
        template = '''
                    You are an expert SQL data analyst, you convert natural language questions into correct and optimised SQL queries.
                    You are working with the following database schema:
                    {schema_database}

                    Description about the database:
                    The Chinook database is a sample SQL database that simulates a digital music store. \
                    It contains tables for artists, albums, tracks, customers, invoices, and employees 

                    Here is the user question:
                    {user_query}

                    Your task outline is:
                    1. Understand the user's query and intent
                    2. Identify the relevant tables and columns
                    3. Join tables correctly if needed
                    4. Filter and aggregate results appropriately
                    5. Return the SQL query only
                    '''
        async def sql_step_logic(sql_prompt_template,recent_question):
            async with cl.Step(name="🔍SQL Query with Guardrails", type="run"):
                structure_llm = llm_model.with_structured_output(SQLOutput)
                sql_generation = sql_prompt_template | structure_llm
                #state['messages'].append(HumanMessage(content=recent_question))
                sql_query_response = sql_generation.invoke({"schema_database":schema_knowledge,"user_query":recent_question})
                return sql_query_response
            
        sql_prompt_template = ChatPromptTemplate.from_template(template)
        recent_question = state['question'].content
        sql_query_response = asyncio.run(sql_step_logic(sql_prompt_template,recent_question))

        print("SQL Query Generated: ",sql_query_response.sql_query)
        state['sql_query'] = sql_query_response.sql_query
        state['sql_query_columns'] = sql_query_response.sql_column_names
        state['next_tool_selection'] = 'sqlexecutor'

        if "sql_query_history" not in state or state["sql_query_history"] is None:
            state["sql_query_history"] = []
        # if "sql_query_reflection_history" not in state or state["sql_query_reflection_history"] is None:
        #     state["sql_query_reflection_history"] = []
        # if 'full_reflection' not in state or state["sql_query_reflection_history"] is None:
        #     state["full_reflection"] = []

        state['sql_query_history'].append(sql_query_response.sql_query)

        state['messages'].append(AIMessage(content=sql_query_response.sql_query,\
                                        additional_kwargs={'pydantic_model':sql_query_response.__class__.__name__}))
        #print("State after SQL generator:",state)
        print("SQL Query Generation stage completed")
        return state
    


    @staticmethod
    def sqlgen_for_eval(user_query):

        template = '''
            You are an expert SQL data analyst, you convert natural language questions into correct and optimised SQL queries.
            You are working with the following database schema:
            {schema_database}

            Description about the database:
            The Chinook database is a sample SQL database that simulates a digital music store. \
            It contains tables for artists, albums, tracks, customers, invoices, and employees 

            Here is the user question:
            {user_query}

            Your task outline is:
            1. Understand the user's query and intent
            2. Identify the relevant tables and columns
            3. Join tables correctly if needed
            4. Filter and aggregate results appropriately
            5. Return the SQL query only
            '''
        sql_prompt_template = ChatPromptTemplate.from_template(template)
        recent_question = user_query.strip()
        structure_llm = llm_model.with_structured_output(SQLOutput)
        sql_generation = sql_prompt_template | structure_llm
        #state['messages'].append(HumanMessage(content=recent_question))
        sql_query_response = sql_generation.invoke({"schema_database":schema_knowledge,"user_query":recent_question})
        print(sql_query_response)
        return sql_query_response.sql_query


if __name__ == "__main__":
    #SQLGenerator = SQLGen_agent()
    state1 = SQLGen_agent.SQLGenerator({'question': HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}), \
                           'messages': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}),\
                                         AIMessage(content='Yes', additional_kwargs={'pydantic_model': 'ClassifyQuestion'}, response_metadata={})], \
                            'question_history': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={})], \
                                                'on_topic_classifier': 'Yes'})
    print("State after sql generator:",state1)

    state2 = SQLGen_agent.sqlgen_for_eval("List all albums released my metallica")
    print("\nResponse:",str(state2),type(state2))