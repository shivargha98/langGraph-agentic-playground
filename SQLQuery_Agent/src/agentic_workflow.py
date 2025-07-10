from state import AgentState
from langgraph.graph import StateGraph,END
from utils import *
from on_topic_classifier import *
from sql_executor import *
from sql_generator import *
from actNode import *
from relfection_node import *
from query_judge import *
from PIL import Image
from langchain_core.runnables.graph import MermaidDrawMethod
import io

workflowGraph = StateGraph(AgentState)
workflowGraph.add_node("topic_classifier",on_topic_classifier)
workflowGraph.add_node("sql_generator",SQLGenerator)
workflowGraph.add_node("sqlgen_reflection",reflect)
workflowGraph.add_node("sql_executor",SQLExecutor)
workflowGraph.add_node("actNode",act)
workflowGraph.add_node("toolNode",execute_tools)
workflowGraph.add_node("judgeLLM",judge_reflect)

def judge_iter(state:AgentState):
    if state['full_reflection_iter'] < 2:
         state['full_reflection_iter'] = state['full_reflection_iter'] + 1
         return "END"
    elif state['full_reflection'][-1]['node_retry'].lower() == 'sqlgenerator':
        return "SQL_GEN"
    elif state['full_reflection'][-1]['node_retry'].lower() == 'toolnode':
        return "TOOL"



def reflect_iter(state:AgentState):
     if state['reflection_iterations'] < 2:
         state['reflection_iterations'] = state['reflection_iterations'] + 1
         return "REFLECT"
     else:
         return "SQLEXEC"
         

def should_end(state:AgentState):

    if state['on_topic_classifier'] == 'No':
        return "END"
    else:
        return "SQL_GEN"

workflowGraph.add_conditional_edges("topic_classifier",
                                    should_end,
                                    {
                                        "END":END,
                                        "SQLGEN":"sql_generator"
                                    })

workflowGraph.add_conditional_edges("sql_generator",reflect_iter,
                                    {
                                        "REFLECT":"sqlgen_reflection",
                                        "SQLEXEC":"sql_executor"

                                    })
workflowGraph.add_edge("sqlgen_reflection","sql_generator")
#workflowGraph.add_edge("sql_generator","sql_executor")
workflowGraph.add_edge("sql_executor","actNode")
workflowGraph.add_edge("actNode","toolNode")
workflowGraph.add_edge("toolNode","judgeLLM")
workflowGraph.add_conditional_edges("judgeLLM",judge_iter,
                                    {
                                        "END":END,
                                        "SQL_GEN":"sql_generator",
                                        "TOOL":"toolNode"

                                    })

workflowGraph.set_entry_point("topic_classifier")
app = workflowGraph.compile()
print('APP compiled')
image = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
##convert bytes to PIL format
image = Image.open(io.BytesIO(image))
image.save("graph.png")