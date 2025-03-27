from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from agents import set_default_openai_client, set_tracing_disabled

client = None

def get_client():
    return client

def isClientLoaded():
    return client is not None

def load_client():
    load_dotenv()
    global client
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    set_tracing_disabled(True)
    set_default_openai_client(client)
    return client