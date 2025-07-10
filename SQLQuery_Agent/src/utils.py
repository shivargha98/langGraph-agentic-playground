from schema_description import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

db_path = 'Chinook_Sqlite.sqlite'
schema_knowledge = describe_schema(db_path)

llm_model = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash',max_retries=2)
llm_qwen_coder = ChatOllama(model="qwen2.5-coder:3b")
llm_judge = ChatGroq(model = 'llama-3.1-8b-instant')
