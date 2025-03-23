import os
from dotenv import load_dotenv
from langsmith import wrappers
import openai


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_client():
    return wrappers.wrap_openai(openai.Client())
    