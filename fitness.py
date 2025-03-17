import base64, time
from openai import OpenAI
from pathlib import Path

from m_funcs import translate, rand_string

import dotenv, os

dotenv.load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def encode_image(image_path):
    """Encodes an image to base64 format."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def diet_plan(base64_image, user_input, extra):
    """Identifies food items from an image of a fridge."""
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You are a nutritionist. Use the food items in the image and in the text to create a diet plan for a user. Try to ensure a balanced, healthy diet, and provide VERY brief recipes."},
            {"role": "user", 
             "content": [
                {"type": "text", 
                 "text": user_input + '\nExtra User Comments: ' + extra},
                {"type": "image_url", 
                 "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]
    )
    return completion.choices[0].message.content

def exercise_plan(diet_plan, extra):
    """Creates a 1-minute workout plan to complement a given diet plan."""
    client = OpenAI(api_key=API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4-turbo", 
        messages=[
            {"role": "system", "content": "Write a script for a workout/yoga plan a personal trainer would read out to instruct a beginner. It should complement the diet plan that the user provides. Do not add any cues, just what they have to say."},
            {"role": "user", "content": diet_plan + '\nExtra User Comments: ' + extra}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text):
    filename=f"static\\workouts\\{rand_string(5)}{int(time.time())}.mp3"
    speech_file_path = Path(filename)
    
    response = client.audio.speech.create(
        model="tts-1",
        voice = "alloy",
        input=text,
        speed=0.9
    )
    response.stream_to_file(speech_file_path)
    return filename

def generate_fitness(base64_image, user_input, extra, lang):
    if lang != 'en':
        user_input = translate(user_input, lang, 'en')
        extra = translate(extra, lang, 'en')
    diet_plan_output = diet_plan(base64_image, user_input, extra)
    diet_plan_output = translate(diet_plan_output, 'en', lang)
    exercise_plan_output = exercise_plan(diet_plan_output, extra)
    exercise_plan_output = translate(exercise_plan_output, 'en', lang)
    audio_file = text_to_speech(exercise_plan_output)
    return audio_file, diet_plan_output, exercise_plan_output