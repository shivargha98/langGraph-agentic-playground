import chainlit as cl
import sqlite3


@cl.on_chat_start
async def start_chat():
    await cl.Message(content="👋 Welcome! Please upload a `.sqlite` DB file to begin.").send()

