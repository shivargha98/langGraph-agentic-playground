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


##### dict of tool description #########
tool_descriptors = {
    "text_listing_tool":"Displays a list of textual entries as bullet points.Use this tool when the SQL result returns only textual data (e.g., names of albums, artists, genres).",
    "bar_chart_tool":"Generates a bar chart from categorical-numeric pairs. Use this tool when the SQL result includes categories (e.g., countries, genres) with corresponding numeric values (e.g., revenue, sales count).",
    "line_chart_tool":"Creates a line chart from time series data.Use this tool when the SQL result includes time-based keys (e.g., months, dates) and numeric values (e.g., monthly sales, revenue)."
}