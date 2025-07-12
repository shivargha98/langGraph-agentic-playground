from agentic_workflow import *

##################### phoenix by arize tracing ########################
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
# Register the tracer provider (Phoenix setup)
tracer_provider = register()
# Instrument LangChain to send traces to Phoenix
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
########################################################################


user_query = input("What is your Query to the Chinook database?")
response = run_workflow(user_query.strip())
print("\n\n .... Agent Session Ended ....")