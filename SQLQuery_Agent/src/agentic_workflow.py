from state import AgentState
from langgraph.graph import StateGraph,END
from utils import *
from on_topic_classifier import *
from sql_executor import *
from sql_generator import *
from actNode import *
from PIL import Image
from langchain_core.runnables.graph import MermaidDrawMethod
import io

workflowGraph = StateGraph(AgentState)
workflowGraph.add_node("topic_classifier",on_topic_classifier)
workflowGraph.add_node("sql_generator",SQLGenerator)
workflowGraph.add_node("sql_executor",SQLExecutor)
workflowGraph.add_node("actNode",act)
workflowGraph.add_node("toolNode",execute_tools)

def should_end(state:AgentState):

    if state['on_topic_classifier'] == 'No':
        return END
    else:
        return "sql_generator"

workflowGraph.set_entry_point("topic_classifier")
workflowGraph.add_conditional_edges("topic_classifier",should_end)
workflowGraph.add_edge("sql_generator","sql_executor")
workflowGraph.add_edge("sql_executor","actNode")
workflowGraph.add_edge("actNode","toolNode")
workflowGraph.add_edge("toolNode",END)
app = workflowGraph.compile()
image = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
##convert bytes to PIL format
image = Image.open(io.BytesIO(image))
image.save("/home/shivargha/langGraph-agentic-playground/SQLQuery_Agent/src/graph.png")