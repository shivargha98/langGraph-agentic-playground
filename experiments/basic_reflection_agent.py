from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()


### check tracing with langsmith ###

llm_model = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash',
                                    temperature = 0,
                                    max_tokens=None,
                                    timeout=None,
                                    max_retries=2)
##Creating a basic generation chain
generation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a twitter sports influencer assistant tasked with writing analytical posts."
        "Generate the most analytical post possible for the user's request."
        "If the user gives a critique, respond with a revised version of the previous attempts."
    ),
    MessagesPlaceholder(variable_name="messages")
    
])
generation_chain = generation_prompt | llm_model


### create a reflection chain ###
reflection_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a tweet grading assistant. Generate critique and recommendations for the input tweet."
        "Always provide detailed recommendations, especially about length,virality,style etc"
        
    ),
    MessagesPlaceholder(variable_name="messages")

    
])
##Message Holder enables to give in messages like 
## template.format(messages=["user","Here's a tweet..."])
reflection_chain = reflection_prompt | llm_model


#### building the message graph ###
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
### creating the message graphs ###
REFLECT = 'reflect'
GENERATE = 'generate'
graph = MessageGraph()

## creating the generateNode ###
##Nodes will take a list of all previous nodes (states) and generate a new response##
def generateNode(state):
    '''
        state : entire state of the previous conversations, (list of messages in the past)
    '''
    return generation_chain.invoke({"messages":state})

def relfectNode(state):
    resp = reflection_chain.invoke({"messages":state})
    ##Reflect node as Human Intervention
    return [HumanMessage(content=resp.content)]
##add nodes generate and reflect
graph.add_node(GENERATE,generateNode)
graph.add_node(REFLECT,relfectNode)
graph.set_entry_point(GENERATE)

def should_continue(state):
    if (len(state)>4):
        return END
    return REFLECT

##Add conditional edge generate either goes to END or Reflect
graph.add_conditional_edges(GENERATE,should_continue)
##Add edge from REFLECT to Generate##
graph.add_edge(REFLECT,GENERATE)
app = graph.compile()

from IPython.display import Image, display
png = app.get_graph().draw_mermaid_png()
display(Image(png))

# response = app.invoke(HumanMessage(content="IPL highest runs and wickets statistics"))
# print(response)

response = app.invoke(HumanMessage(content="IPL highest runs and wickets statistics"))
print(response)