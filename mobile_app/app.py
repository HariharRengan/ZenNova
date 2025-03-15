from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import random, string, os, time
from deep_translator import GoogleTranslator
from openai import OpenAI
from pydub import AudioSegment
import requests


API_KEY = "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"
client = OpenAI(api_key=API_KEY)

app = FastAPI()  # ✅ Make sure this exists

BASE_URL = "http://192.168.70.197:8000"

STATIC_DIR = Path("static/meditaters")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

tracks = ['ambient', 'eastern', 'nature']

def rand_string(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

class MeditationRequest(BaseModel):
    user_day: str
    feeling: str
    track: str
    lang: str

def translate(text, lang1, lang2):
    translator = GoogleTranslator(source=lang1, target=lang2)
    return translator.translate(text)

def generate_meditation_script(user_prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo", 
        messages=[
            {"role": "system", "content": "You are a meditation script writer. Generate a calming and personalized meditation script with pauses."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content


def text_to_speech(text):
    # Ensure the directory exists before saving
    output_dir = Path("static/meditaters")
    output_dir.mkdir(parents=True, exist_ok=True)  # ✅ Automatically creates folder if missing

    filename = output_dir / f"{rand_string(5)}{int(time.time())}.mp3"

    response = client.audio.speech.create(
        model="tts-1",
        voice="sage",
        input=text,
        speed=0.9
    )
    response.stream_to_file(str(filename))  # ✅ Convert Path object to string

    return str(filename)

def select_background_audio(track):
    return f"audio/background_audio.mp3" 

    #Removed the Audio Functionality for Now

def mix_audio(speech_file, background_file):
    output_file = f"static/meditaters/{rand_string(5)}{int(time.time())}_f.mp3"

    speech = AudioSegment.from_file(speech_file)
    background = AudioSegment.from_file(background_file).set_frame_rate(speech.frame_rate)
    background = background - 15  
    mixed = background.overlay(speech)
    mixed.export(output_file, format="mp3")

    os.remove(speech_file)
    return output_file

def generate_cover_image(user_prompt):
    prompt = f"Generate a calming meditation cover image based on the feeling: {user_prompt}. NO TEXT AT ALL."
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    return response.data[0].url

@app.post("/generate-meditation/")
def generate_meditation(request: MeditationRequest):
    """Generates a meditation audio and cover image, then saves them properly."""
    
    # ✅ Translate user input
    user_day = translate(request.user_day, request.lang, "en")
    user_prompt = f"I am feeling {request.feeling} today and I would like to meditate on {user_day}."
    
    # ✅ Generate Meditation Audio
    script = generate_meditation_script(user_prompt)
    script = translate(script, "en", request.lang)
    speech_file = text_to_speech(script)
    background_audio = select_background_audio(request.track)
    mixed_audio = mix_audio(speech_file, background_audio)  # ✅ This is a local file path

    # ✅ Generate Cover Image
    cover_image_url = generate_cover_image(request.feeling)

    # ✅ Save Cover Image with Unique Filename
    cover_filename = f"cover_{int(time.time())}.png"
    cover_filepath = STATIC_DIR / cover_filename

    response = requests.get(cover_image_url)
    if response.status_code == 200:
        with open(cover_filepath, "wb") as f:
            f.write(response.content)
    
    # ✅ NO NEED to download `mixed_audio` – it is already a local file
    audio_filename = Path(mixed_audio).name  # Extract filename from full path

    # ✅ Return proper URLs so Swift can load them
    return {
        "audio_url": f"{BASE_URL}/static/meditaters/{audio_filename}",
        "cover_url": f"{BASE_URL}/static/meditaters/{cover_filename}"
    }

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
