from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from state import *
from tools import *
from utils import *


def reactNode(state:AgentState):
    tools = [text_listing_tool, bar_chart_tool, line_chart_tool]
    llm_with_tools = llm_model.bind_tools(tools)
    
    ACT_PROMPT = '''
    You are a data visualization agent. Based on the following context, choose the appropriate tool from one of the following:
    - `bar_chart_tool`: use when one column is categorical (like names, genres) and another is numeric.
    - `line_chart_tool`: use when one column is a time/date and another is numeric (e.g., monthly revenue).
    - `text_listing_tool`: use when data is purely text-based.
    
    Respond by calling the correct tool with the appropriate SQL result data.
    
    ---
    
    User Query: {user_query}
    
    LLM's SQL Response: {ai_message}
    
    SQL Query Result (sample): {sql_result}
    
    Column Names: {column_names}
    '''
    
    prompt_template = ChatPromptTemplate.from_template(ACT_PROMPT)
    chain = prompt_template | llm_with_tools
    ai_message = chain.invoke({'user_query':state['messages'][-2].content,
                 'ai_message':state['messages'][-1].content,
                 'sql_result':state['sql_result'][-1],
                 'column_names':state['sql_query_columns']})
    state['messages'].append(ai_message)
    return state


def execute_tools(state:AgentState):

    tools = [text_listing_tool, bar_chart_tool, line_chart_tool]
    tools_by_name = {tool.name: tool for tool in tools}

    ##check for ai message##
    if isinstance(state['messages'][-1],AIMessage):
        ai_message = state['messages'][-1]
        if hasattr(ai_message,"tool_calls"):
            tool_messages = []
            for tool_call in ai_message.tool_calls:
                tool_call_function = tool_call['name']
                call_id = tool_call["id"]

                