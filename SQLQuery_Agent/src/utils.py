from schema_description import *
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

db_path = '/home/shivargha/langGraph-agentic-playground/SQLQuery_Agent/Chinook_Sqlite.sqlite'
schema_knowledge = describe_schema(db_path)

llm_model = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash',max_retries=2)
