from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from pydantic import BaseModel, Field
from state import AgentState
from typing import List
from utils import *

class SQLOutput(BaseModel):
    sql_query:str = Field(...,description="SQL Query generated")
    sql_column_names:List[str] = Field(...,description = "List of column names after data extraction")

def SQLGenerator(state:AgentState):
    print("inside the SQLGenerator agent; state at the moment:",state)


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
    recent_question = state['question'].content
    structure_llm = llm_model.with_structured_output(SQLOutput)
    sql_generation = sql_prompt_template | structure_llm
    #state['messages'].append(HumanMessage(content=recent_question))
    sql_query_response = sql_generation.invoke({"schema_database":schema_knowledge,"user_query":recent_question})
    print(sql_query_response)
    state['sql_query'] = sql_query_response.sql_query
    state['sql_query_columns'] = sql_query_response.sql_column_names
    state['next_tool_selection'] = 'sqlexecutor'

    if "sql_query_history" not in state or state["sql_query_history"] is None:
        state["sql_query_history"] = []

    state['sql_query_history'].append(sql_query_response.sql_query)

    state['messages'].append(AIMessage(content=sql_query_response.sql_query,\
                                       additional_kwargs={'pydantic_model':sql_query_response.__class__.__name__}))
    return state


if __name__ == "__main__":
    state1 = SQLGenerator({'question': HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}), \
                           'messages': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}),\
                                         AIMessage(content='Yes', additional_kwargs={'pydantic_model': 'ClassifyQuestion'}, response_metadata={})], \
                            'question_history': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={})], \
                                                'on_topic_classifier': 'Yes'})
    print("State after sql generator:",state1)