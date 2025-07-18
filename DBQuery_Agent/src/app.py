import chainlit as cl
import asyncio
from schema_description import *
from agentic_workflow import *
from dotenv import load_dotenv
import uuid
import plotly.io as pio
import plotly.graph_objects as go
from on_topic_classifier import *


load_dotenv()


##################### phoenix by arize tracing ########################
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
# Register the tracer provider (Phoenix setup)
tracer_provider = register()
# Instrument LangChain to send traces to Phoenix
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
########################################################################

app = build_graph()
thread_id = str(uuid.uuid4())

# @cl.on_chat_start
# async def start_chat():
#     await cl.Message(content="👋 Welcome! Please upload a `.sqlite` DB file to begin.").send()
#     cl.user_session.set("thread_id", thread_id)
    #cl.user_session["thread_id"] = thread_id

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Total sales by Country",
            message="Can you Show total sales for each country",
            ),

        cl.Starter(
            label="Monthly Revenue",
            message="Show monthly revenue from invoice sales",
            ),
        ]

@cl.step(type="Agent")
async def SQLAgent():
    # Simulate a running task
    await cl.sleep(2)

    return "Done"


@cl.on_message
async def on_message(msg: cl.Message):

    cl.user_session.set("thread_id", thread_id)
    print("The user sent:", msg)
    #await cl.Message(content=f"Human Message: {msg.content}").send()
    # for file in msg.elements:
    #     print(file.path)
    # thinking = cl.Message(content="🤔 Thinking...")
    # await thinking.send()
    if cl.user_session.get("db_file_path") is None:
        db_file_path = msg.elements[0].path
        cl.user_session.set("db_file_path",db_file_path)
    else:
        db_file_path = cl.user_session.get("db_file_path")

    #tool_res = await tool()
    
    schema_desc =  describe_schema(db_file_path)
    # question_tool = TopicClassifier.on_topic_classifier()
    
    #print(str(schema_desc))

    with open("schema_file.txt","w",encoding="utf-8") as f:
        f.write(str(schema_desc))
    f.close()

    user_query = msg.content.strip()
    #thread_id = cl.user_session.id
    print(thread_id)
    response = run_workflow(user_query.strip(),app,thread_id)
    response_msg = response["messages"][-1].content
    
    image = cl.Image(path="D:\langGraph-agentic-playground\DBQuery_Agent\chart2.png", name="Visualization", display="inline",size="large")
    await cl.Message(
        content="✨ Done crunching the numbers! Here's what I found:",
        elements=[image]
    ).send()
