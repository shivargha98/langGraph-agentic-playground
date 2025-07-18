from state import AgentState
from langgraph.graph import StateGraph,END
from utils import *
from on_topic_classifier import *
from sql_executor import *
from sql_generator import *
from actNode import *
from reflection_node import *
from sql_guardrail import *
from query_judge import *
from PIL import Image
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.runnables.graph import MermaidDrawMethod
import io
import os
import agentops
from agentops.sdk.decorators import session,workflow
from dotenv import load_dotenv
load_dotenv()

AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
agentops.init(
    api_key=AGENTOPS_API_KEY,
    default_tags=['custom integration'],
    auto_start_session=False
)

#workflowGraph = StateGraph(AgentState)
memory = MemorySaver()




def end_node(state:AgentState):

    #print(state)
    if state['on_topic_classifier'] == 'No':
        #print(AIMessage(content="Off Topic Question"))
        state['messages'].append(AIMessage(content="Off Topic Question"))

    elif state['guardrail_validation'][-1] == "validation_failed":
        #print(AIMessage(content="Guard Failed, DELETE or DROP query detected"))
        state['messages'].append(AIMessage(content="Guard Failed, DELETE or DROP query detected in SQL query"))
    else:
        #print(AIMessage(content="Analytics generated"))
        #print("HIII",state['messages'])
        state['messages'].append(AIMessage(content="All steps followed, llm judged and analytics generated"))

    return state
        


def judgellm_decide(state:AgentState):
    #state['full_reflection_iter'] = state['full_reflection_iter'] + 1
    # if state['full_reflection_iter'] <= 1:
    #      return "END"
    if state['full_reflection'][-1]['node_retry'].lower() == "none":
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
         #return "REFLECT"
         return "GUARD"

def should_end(state:AgentState):

    if state['on_topic_classifier'] == 'No':
        return "END"
    else:
        return "SQL_GEN"
    

def guardrail_logic(state:AgentState):
    if state['guardrail_validation'][-1] == "validation_success":
        return "REFLECT"
    else:
        return "END"

@workflow(name="build_sql_graph")
def build_graph():

    workflowGraph = StateGraph(AgentState)
    
    workflowGraph.add_node("topic_classifier",TopicClassifier.on_topic_classifier)
    workflowGraph.add_node("sql_generator",SQLGen_agent.SQLGenerator)
    workflowGraph.add_node("sql_guardrail",SQL_guard)
    workflowGraph.add_node("sql_query_reflection",SQL_query_reflect.reflect)
    workflowGraph.add_node("sql_executor",SQLExecutor)
    workflowGraph.add_node("actNode",ReACT.act)
    workflowGraph.add_node("toolNode",ReACT.execute_tools)
    workflowGraph.add_node("judgeLLM",LLM_judge.judge_reflect)
    workflowGraph.add_node("end_node",end_node)


    workflowGraph.add_conditional_edges("topic_classifier",
                                        should_end,
                                        {
                                            "END":"end_node",
                                            "SQL_GEN":"sql_generator"
                                        })
    


    workflowGraph.add_conditional_edges("sql_generator",sqlreflect_decide,
                                        {
                                            "GUARD":"sql_guardrail",
                                            "SQLEXEC":"sql_executor"

                                        })
    

    workflowGraph.add_conditional_edges("sql_guardrail",guardrail_logic,
                                        {
                                            "REFLECT":"sql_query_reflection",
                                            "END":"end_node"

                                        })
    
    workflowGraph.add_edge("sql_query_reflection","sql_generator")
    #workflowGraph.add_edge("sql_generator","sql_executor")
    workflowGraph.add_edge("sql_executor","actNode")
    workflowGraph.add_edge("actNode","toolNode")
    workflowGraph.add_edge("toolNode","judgeLLM")
    workflowGraph.add_conditional_edges("judgeLLM",judgellm_decide,
                                        {
                                            "END":"end_node",
                                            "SQL_GEN":"sql_generator",
                                            "TOOL":"toolNode"

                                        })
    
    workflowGraph.add_edge("end_node",END)

    workflowGraph.set_entry_point("topic_classifier")
    app = workflowGraph.compile(checkpointer=memory)
    print('APP compiled')
    image = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    ##convert bytes to PIL format
    image = Image.open(io.BytesIO(image))
    image.save("graph.png")
    print("Image saved")

    return app



@session(name="SQL_Agent_Trace")
def run_workflow(user_query,app,thread_id):

    
    config = {"configurable":{
        "thread_id":thread_id}}
    response = app.invoke({'question':HumanMessage(content=user_query)},config)
    #print(response)
    return response

if __name__ == "__main__":
    app = build_graph()