from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from pydantic import BaseModel, Field
from state import AgentState
from typing import List
from utils import *
import sqlite3
import json
import asyncio
from agentops.sdk.decorators import tool
import chainlit as cl

@tool(name='SQL_query_executor')
@cl.step(name="Executor")
def SQLExecutor(state:AgentState):

    print("\nSQL Execution on Database")
    if state['next_tool_selection'] == 'sqlexecutor':
        if "sql_result_history" not in state or state["sql_result_history"] is None:
            state["sql_result_history"] = []

        sql_query_code = state['sql_query']
        try:
            async def sql_exec_logic():
                async with cl.Step(name="🔍SQL Execution", type="run"):
                    conn = sqlite3.connect(db_path)
                    result = conn.execute(sql_query_code).fetchall()
                    return result
            
            #print("res:",result)
            result = asyncio.run(sql_exec_logic())
            if len(state['sql_query_columns']) == 1:
                #print([i[0] for i in result])
                result = [i[0] for i in result]
                state['sql_result'] = json.dumps(result)

            else:
                data1 = []
                data2 = []
                col_names_reindexed = []
                for i in result:
                    if len(i) > 1:
                        data1.append(i[0])
                        data2.append(i[1])
                #print(data1,data2)
                column_names = state['sql_query_columns']
                title = state['question'].content

                ##############################################################
                
                if all(isinstance(x, str) for x in data1):
                    #print('1a')
                    if all(isinstance(x, int) for x in data2):
                        #print('1b')
                        dict_data = {k:v for k,v in zip(data1,data2)}
                        col_names_reindexed = column_names
                        state['sql_result'] = json.dumps(dict_data)
                        #state['sql_query_columns']
                    elif all(isinstance(x, float) for x in data2):
                        #print('1b')
                        dict_data = {k:v for k,v in zip(data1,data2)}
                        col_names_reindexed = column_names
                        state['sql_result'] = json.dumps(dict_data)
                        
                elif all(isinstance(x, str) for x in data2):
                    if all(isinstance(x, int) for x in data1):
                        dict_data = {k:v for k,v in zip(data2,data1)}
                        col_names_reindexed = column_names[::-1]
                        state['sql_result'] = json.dumps(dict_data)
                        state['sql_query_columns'] = col_names_reindexed
                        
                    elif all(isinstance(x, float) for x in data1):
                        dict_data = {k:v for k,v in zip(data2,data1)}
                        col_names_reindexed = column_names[::-1]
                        state['sql_result'] = json.dumps(dict_data)
                        state['sql_query_columns'] = col_names_reindexed

            ###################################################################################
            state['sql_result_history'].append(state['sql_result'])        
            #print("\nState after sq EXEC:",state)   
            print("SQL Execution Completed Successfully")     
            return state
        except Exception as error:
            #state['sql_result'].append(json.dumps(result))
            print(error)
            print("SQL Execution Failed") 
            return state

if __name__ == "__main__":
    state = {'question': HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}),\
            'messages': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}), AIMessage(content='Yes', additional_kwargs={'pydantic_model': 'ClassifyQuestion'}, response_metadata={}), AIMessage(content='SELECT Album.Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"', additional_kwargs={'pydantic_model': 'SQLOutput'}, response_metadata={})],\
            'question_history': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={})], \
            'on_topic_classifier': 'Yes', 'sql_query': 'SELECT Album.Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"', \
                'sql_query_columns': ['AlbumTitle'], 'next_tool_selection': 'sqlexecutor', 'sql_query_history': ['SELECT Album.Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"']}
    state_after_sqlexec = SQLExecutor(state)
    print(state_after_sqlexec)
