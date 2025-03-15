import openai
from openai import OpenAI

import dotenv
import os

dotenv.load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()

def create_profile(sleep_data):
    prompt = """you are a sleep analyst. summarise the following data into an information rich paragraph that creates a custum sleep profile for the user based on the following 1-night sleep data
    dont give any feedback. just summarise the data. and do sleep duration in hours
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # Use the latest available model
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": sleep_data}
        ]
    )
    return response.choices[0].message.content
