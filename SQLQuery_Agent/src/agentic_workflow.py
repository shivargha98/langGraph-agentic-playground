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
from langchain_core.messages import HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
import io

workflowGraph = StateGraph(AgentState)
workflowGraph.add_node("topic_classifier",on_topic_classifier)
workflowGraph.add_node("sql_generator",SQLGenerator)
workflowGraph.add_node("sql_query_reflection",reflect)
workflowGraph.add_node("sql_executor",SQLExecutor)
workflowGraph.add_node("actNode",act)
workflowGraph.add_node("toolNode",execute_tools)
workflowGraph.add_node("judgeLLM",judge_reflect)

def judgellm_decide(state:AgentState):
    #state['full_reflection_iter'] = state['full_reflection_iter'] + 1
    # if state['full_reflection_iter'] <= 1:
    #      return "END"
    if len(state['full_reflection']) == 1:
        return "END"
    else:
        if state['full_reflection'][-1]['node_retry'].lower() == 'sqlgenerator':
            return "SQL_GEN"
        elif state['full_reflection'][-1]['node_retry'].lower() == 'toolnode':
            return "TOOL"



def sqlreflect_decide(state:AgentState):
     #state['reflection_iterations'] = state['reflection_iterations'] + 1
     if len(state['sql_query_reflection_history']) ==1:
         #print("reflection_iterations:",state['reflection_iterations'])
         return "SQLEXEC"
     else:
         return "REFLECT"
         

def should_end(state:AgentState):

    if state['on_topic_classifier'] == 'No':
        return "END"
    else:
        return "SQL_GEN"

workflowGraph.add_conditional_edges("topic_classifier",
                                    should_end,
                                    {
                                        "END":END,
                                        "SQL_GEN":"sql_generator"
                                    })

workflowGraph.add_conditional_edges("sql_generator",sqlreflect_decide,
                                    {
                                        "REFLECT":"sql_query_reflection",
                                        "SQLEXEC":"sql_executor"

                                    })
workflowGraph.add_edge("sql_query_reflection","sql_generator")
#workflowGraph.add_edge("sql_generator","sql_executor")
workflowGraph.add_edge("sql_executor","actNode")
workflowGraph.add_edge("actNode","toolNode")
workflowGraph.add_edge("toolNode","judgeLLM")
workflowGraph.add_conditional_edges("judgeLLM",judgellm_decide,
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
print("Image saved")


response = app.invoke({'question':HumanMessage(content="Show Total sales for each country")})
print(response)