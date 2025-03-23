import os
from dotenv import load_dotenv
import openai


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_openai_client():
    return openai.Client()
