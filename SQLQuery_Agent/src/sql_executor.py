from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from pydantic import BaseModel, Field
from state import AgentState
from typing import List
from utils import *
import json

def SQLExecutor(state:AgentState):
    if state['next_tool_selection'] == 'sqlexecutor':
        sql_query_code = state['sql_query']
        try:
            conn = sqlite3.connect(db_path)
            result = conn.execute(sql_query_code).fetchall()
            state['sql_result'].append(json.dumps(result))
            return state
        except:
            state['sql_result'].append(json.dumps(result))
            return state

if __name__ == "__main__":
    state_after_sqlgen = {'messages': [HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}),
                AIMessage(content='SELECT Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"', additional_kwargs={}, response_metadata={})],
                'sql_result': [],
                'question': HumanMessage(content='List all albums released my metallica', additional_kwargs={}, response_metadata={}),
                'sql_query': 'SELECT Title FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = "Metallica"',
                'sql_query_columns': ['Title'],
                'next_tool_selection': 'sqlexecutor'}
    state_after_sqlexec = SQLExecutor(state_after_sqlgen)
    print(state_after_sqlexec)