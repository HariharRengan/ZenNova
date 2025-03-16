import openai
from openai import OpenAI

import dotenv
import os

dotenv.load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY

def generate_therapy(user_prompt, history):
    client = OpenAI(api_key=API_KEY)
    chat_history = [{"role": "user" if i % 2 == 0 else "assistant", "content": message} for i, message in enumerate(history)]
    response = client.chat.completions.create(
        model="gpt-4-turbo", 
        messages=[{"role": "system", "content": "You are a therapist. Provide a response to a patient seeking therapy. Make your responses short, below 30 tokens"}] + chat_history + [{"role": "user", "content": user_prompt}],
        max_tokens=30
    )
    return response.choices[0].message.content