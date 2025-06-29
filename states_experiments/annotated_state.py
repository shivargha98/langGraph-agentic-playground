from typing import TypedDict,List,Annotated
from langgraph.graph import END,StateGraph
import operator

class SimpleState(TypedDict):
    ## This is the blueprint of the State ##  
    count: int
    sum: Annotated[int,operator.add]
    history_count: Annotated[List[int], operator.concat]
    history_sum: Annotated[List[int] , operator.concat]
    
### Normal message graph would only have a list of messages
def increment(state:SimpleState) -> SimpleState:
    ##function takes in a state returns a modified state##
    ##Manual State Transformation
    new_count = state['count'] + 1
    return {

        'count': new_count,
        'sum': new_count, ##sum of all new_counts via operator.add,new value of new_count gets added
        'history_count': [new_count], ##update via list + list,new value of new_count gets concat as list
        'history_sum': [state['sum'] + new_count]
    }

def should_continue(state):
    if(state["count"] < 5):
        return "continue"
    else:
        return "stop"

graph = StateGraph(SimpleState)
graph.add_node("increment",increment)
graph.add_conditional_edges("increment",
                            should_continue,
                            {
                                "continue":"increment",
                                "stop":END
                                ### if *continue* then go to increment
                                ### if *stop* then go to END
                            })
#####
graph.set_entry_point("increment")
app = graph.compile()
print(app.get_graph().draw_mermaid())

state = {'count':0,
        'sum':0,
        'history_count':[],
        'history_sum':[]}
         ##intital state##
res = app.invoke(state)
#####
print(res)


'''
FLOWCHART
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
        __start__([<p>__start__</p>]):::first
        increment(increment)
        __end__([<p>__end__</p>]):::last
        __start__ --> increment;
        increment -. &nbsp;stop&nbsp; .-> __end__;
        increment -. &nbsp;continue&nbsp; .-> increment;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc

'''


