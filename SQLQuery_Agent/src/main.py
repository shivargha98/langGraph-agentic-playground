from agentic_workflow import *
user_query = input("What is your Query to the Chinook database?")
response = run_workflow(user_query.strip())
print("\n\n .... Agent Session Ended ....")