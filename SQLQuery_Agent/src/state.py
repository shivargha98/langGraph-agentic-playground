from typing import TypedDict, List, Annotated, Union, Dict, Any
from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
from langgraph.graph import StateGraph, END, add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage],add_messages]
    question: HumanMessage
    on_topic_classifier: str ##on topic or off topic classifier
    next_tool_selection: Union[str,None]
    sql_query: Union[str,None] ##stores the SQL syntax###
    sql_query_columns: List[str]
    sql_result: Annotated[List[str],operator.concat]