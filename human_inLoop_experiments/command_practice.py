from langgraph.graph import StateGraph, END, START
from langgraph.types import Command
from typing import TypedDict, List

class State(TypedDict):
    text: str

def nodeA(state: State):
    print("A")
    return Command(
        goto="nodeB",
        update={"text":state['text']+'a'}
    )

def nodeB(state:State):
    print('B')
    return Command(
        goto="nodeC",
        update={"text":state['text']+"b"}

    )

def nodeC(state:State):
    print('C')
    return Command(
        goto=END,
        update={"text":state['text']+"c"}

    )

graph = StateGraph(State)
graph.add_node("nodeA",nodeA)
graph.add_node("nodeB",nodeB)
graph.add_node("nodeC",nodeC)
graph.set_entry_point("nodeA")

app = graph.compile()
response = app.invoke({"text":""})


