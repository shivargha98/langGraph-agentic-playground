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
            
            print(result)
            
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
                print(data1,data2)
                column_names = state['sql_query_columns']
                title = state['question'].content

                ##############################################################
                
                if all(isinstance(x, str) for x in data1):
                    print('1a')
                    if all(isinstance(x, int) for x in data2):
                        print('1b')
                        dict_data = {k:v for k,v in zip(data1,data2)}
                        col_names_reindexed = column_names
                        state['sql_result'] = json.dumps(dict_data)
                        #state['sql_query_columns']
                    elif all(isinstance(x, float) for x in data2):
                        print('1b')
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
                                
            return state
        except Exception as error:
            #state['sql_result'].append(json.dumps(result))
            print(error)
            return state

if __name__ == "__main__":
    state = {'messages': [HumanMessage(content='Show monthly revenue from invoice sales', additional_kwargs={}, response_metadata={}),
            AIMessage(content="SELECT strftime('%Y-%m', InvoiceDate) AS month, SUM(Total) AS revenue FROM Invoice GROUP BY month ORDER BY month;", additional_kwargs={}, response_metadata={})],
            'sql_result': '',
            'question': HumanMessage(content='Show monthly revenue from invoice sales', additional_kwargs={}, response_metadata={}),
            'sql_query': "SELECT strftime('%Y-%m', InvoiceDate) AS month, SUM(Total) AS revenue FROM Invoice GROUP BY month ORDER BY month;",
            'sql_query_columns': ['month', 'revenue'],
            'next_tool_selection': 'sqlexecutor'}
    state_after_sqlexec = SQLExecutor(state)
    print(state_after_sqlexec)
