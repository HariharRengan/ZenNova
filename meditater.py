from pydub import AudioSegment
from pathlib import Path
import random, string

import openai
from openai import OpenAI

from deep_translator import GoogleTranslator

import dotenv
import os
import time

dotenv.load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY
tracks = ['ambient', 'eastern', 'nature']

client = OpenAI()

def rand_string(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def translate(text, lang1, lang2):
    translator = GoogleTranslator(source=lang1, target=lang2)
    translated_text = translator.translate(text)
    return translated_text

def generate_meditation_script(user_prompt):
    client = OpenAI(api_key=API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4-turbo", 
        messages=[
            {"role": "system", "content": "You are a meditation script writer. Generate a calming and personalized meditation script with pauses."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text):
    filename=f"static\\meditaters\\{rand_string(5)}{int(time.time())}.mp3"
    speech_file_path = Path(filename)
    
    response = client.audio.speech.create(
        model="tts-1",
        voice = "alloy",
        input=text,
        speed=0.9
    )
    response.stream_to_file(speech_file_path)
    return filename

def select_background_audio(track):
    # return 'audio\\' + (track if track != 'random' else random.choice(tracks)) + '.mp3'
    return 'audio\\' + 'background_audio' + '.mp3'

def mix_audio(speech_file_path, background_file_path):
    """Mixes speech with background music into one audio file."""

    output_file=f"static\\meditaters\\{rand_string(5)}{int(time.time())}_f.mp3"

    if isinstance(speech_file_path, AudioSegment):
        raise TypeError("Expected a file path, but got an AudioSegment object for speech_file.")
    if isinstance(background_file_path, AudioSegment):
        raise TypeError("Expected a file path, but got an AudioSegment object for background_file.")
    
    speech = AudioSegment.from_file(speech_file_path)
    background = AudioSegment.from_file(background_file_path).set_frame_rate(speech.frame_rate)
    background = background - 15  
    mixed = background.overlay(speech)
    mixed.export(output_file, format="mp3")
    os.remove(speech_file_path)
    return output_file

def generate_cover_image(user_prompt):
    prompt =  f""" Generate a visually appealing cover image for a meditation audio that aligns with the user's current emotional state. 
    Here is how the user is feeling: \n{user_prompt} NO TEXT AT ALL NO TEXT AT ALL NO TEXT AT ALL 
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    return response.data[0].url

def main(user_day, feeling, track, lang):
    t = time.time()
    print(f'{0.01 * int(100 * (time.time() - t))} Initializing meditater...')
    user_day = translate(user_day, lang, "en")
    user_prompt = f"I am feeling {feeling} today and I would like to meditate on {user_day}."
    meditation_script = generate_meditation_script(user_prompt)
    meditation_script = translate(meditation_script, "en", lang)
    print(f'{0.01 * int(100 * (time.time() - t))} Meditation script generated...')
    speech_file = text_to_speech(meditation_script)
    print(f'{0.01 * int(100 * (time.time() - t))} Text converted to speech...')
    background_audio = select_background_audio(track)
    mixed_audio = mix_audio(speech_file, background_audio)
    print(f'{0.01 * int(100 * (time.time() - t))} Meditation audio generated...')
    cover_image = generate_cover_image(feeling)
    print(f'{0.01 * int(100 * (time.time() - t))} Cover image generated...')
    return mixed_audio.replace('\\', '/'), cover_image