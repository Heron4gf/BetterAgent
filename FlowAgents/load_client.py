from openai import OpenAI
from dotenv import load_dotenv

client = None

def isClientLoaded():
    return client is not None

def load_client():
    load_dotenv()
    global client
    client = OpenAI()
    return client