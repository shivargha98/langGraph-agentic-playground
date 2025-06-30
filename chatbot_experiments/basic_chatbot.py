##basic chatbot using groq and LLama##
from typing import TypedDict,Annotated,List
from langgraph.graph import add_messages,StateGraph,END
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage,HumanMessage
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()
llm_model = ChatGroq(model = 'llama-3.1-8b-instant')

class BasicChatState(TypedDict):
    messages: Annotated[List[str],add_messages]

def chatNode(state:BasicChatState):
    return {
        "messages": [llm_model.invoke(state["messages"])] 
    }

"""state["messages"] is a list of BaseMessages (e.g., HumanMessage, SystemMessage, etc.)
Invoke the llm_model on those messages using llm_model.invoke(...)
The result ~ AIMessage is wrapped in a new "messages" list and added to the new state"""



##Creating the entire graph##
graph = StateGraph(BasicChatState)
## add the single chatnode ##
graph.add_node("chatnode",chatNode)
graph.set_entry_point("chatnode")
graph.add_edge("chatnode",END)
app = graph.compile()
image = app.get_graph().draw_mermaid_png()
##convert bytes to PIL format
image = Image.open(io.BytesIO(image))
image.save("chatbot_experiments/basic_chatbot.png")

###looping the chatbot###

## graph is restarting at every while loop ##


while True:
    user_input = input("User: ")
    if (user_input in ["exit","end"]):
        break
    else:
        result = app.invoke(

            {"messages":[HumanMessage(content=user_input)]} ##start with the Human message
        )

        print(result)

'''
The first node in your LangGraph gets this state:
state = {
    "messages": [HumanMessage(...)]
}
Your node (e.g., chatNode) does:
llm_response = llm_model.invoke(state["messages"])

'''