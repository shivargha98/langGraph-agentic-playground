from agentic_workflow import *

##################### phoenix by arize tracing ########################
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
# Register the tracer provider (Phoenix setup)
tracer_provider = register()
# Instrument LangChain to send traces to Phoenix
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
########################################################################


# user_query = input("What is your Query to the Chinook database?")
# response = run_workflow(user_query.strip())
### config using the thread id ###

app = build_graph()
while True:

    print('What is your Query to the Chinook database?')
    user_query = input("User: ")
    if user_query.lower() in ['end','exit']:
        break
    else:
        response = run_workflow(user_query.strip(),app)
        print("AI: " + response["messages"][-1].content)
        
print("\n\n .... Agent Session Ended ....")