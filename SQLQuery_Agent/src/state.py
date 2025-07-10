from typing import TypedDict, List, Annotated, Union, Dict, Any
from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
from langgraph.graph import StateGraph, END, add_messages
import operator


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage],add_messages]
    question: HumanMessage
    question_history: Annotated[List[HumanMessage],add_messages]
    on_topic_classifier: str ##on topic or off topic classifier
    tool_selection_history: List[str]
    sql_query:str  #Union[str,None] ##stores the SQL syntax###
    sql_query_columns: List[str]
    sql_result:str #Annotated[List[str],operator.concat]
    sql_query_history: Annotated[List[str],operator.concat]
    sql_result_history: Annotated[List[str],operator.concat]
    sql_query_reflection_history: Annotated[List[HumanMessage],add_messages]
    reflection_iterations: int
    full_reflection_iter: int
    full_reflection: List[Dict[str,Any]]