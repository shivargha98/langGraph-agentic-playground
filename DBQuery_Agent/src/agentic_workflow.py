from state import AgentState
from langgraph.graph import StateGraph,END
from utils import *
from on_topic_classifier import *
from sql_executor import *
from sql_generator import *
from actNode import *
from reflection_node import *
from query_judge import *
from PIL import Image
from langchain_core.messages import HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
import io
import os
import agentops
from agentops.sdk.decorators import session,workflow

AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
agentops.init(
    api_key=AGENTOPS_API_KEY,
    default_tags=['custom integration'],
    auto_start_session=False
)

workflowGraph = StateGraph(AgentState)


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
    
@workflow(name="build_sql_graph")
def build_graph():

    
    workflowGraph.add_node("topic_classifier",TopicClassifier.on_topic_classifier)
    workflowGraph.add_node("sql_generator",SQLGen_agent.SQLGenerator)
    workflowGraph.add_node("sql_query_reflection",SQL_query_reflect.reflect)
    workflowGraph.add_node("sql_executor",SQLExecutor)
    workflowGraph.add_node("actNode",ReACT.act)
    workflowGraph.add_node("toolNode",ReACT.execute_tools)
    workflowGraph.add_node("judgeLLM",LLM_judge.judge_reflect)


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

    return app



@session(name="SQL_Agent_Trace")
def run_workflow(user_query):

    app = build_graph()
    response = app.invoke({'question':HumanMessage(content=user_query)})
    print(response)
    return response