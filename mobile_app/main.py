from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pathlib import Path
import os
import openai
from openai import OpenAI
import requests



API_KEY = "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"
openai.api_key = API_KEY
background_audio1 = "background_audio.mp3"


def generate_meditation_script(user_prompt):
    client = OpenAI(api_key=API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # Use the latest available model
        messages=[
            {"role": "system", "content": "You are a meditation script writer. Generate a calming and personalized meditation script with pauses."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, filename="meditation_speech.mp3"):
    client = OpenAI(api_key=API_KEY)
    speech_file_path = Path(filename)
    
    response = client.audio.speech.create(
        model="tts-1",
        voice = "alloy",
        input=text,
    )
    response.stream_to_file(speech_file_path)
    return filename

def select_background_audio():
    return background_audio1

def mix_audio(speech_file_path, background_file_path, output_file="final_meditation.mp3"):
    """Mixes speech with background music into one audio file."""
    
    # Ensure paths are strings, not AudioSegment objects
    if isinstance(speech_file_path, AudioSegment):
        raise TypeError("Expected a file path, but got an AudioSegment object for speech_file.")
    
    if isinstance(background_file_path, AudioSegment):
        raise TypeError("Expected a file path, but got an AudioSegment object for background_file.")
    
    # Load audio files
    speech = AudioSegment.from_file(speech_file_path)
    background = AudioSegment.from_file(background_file_path).set_frame_rate(speech.frame_rate)

    # Reduce background volume so the speech is clear
    background = background - 15  
    
    # Overlay speech onto background music
    mixed = background.overlay(speech)
    
    # Export final audio
    mixed.export(output_file, format="mp3")
    
    return output_file

def create_meditation(user_prompt, person_feeling):
    image = generate_cover_image(person_feeling)
    # script = generate_meditation_script(user_prompt)
    # speech_file = text_to_speech(script)
    background_file = select_background_audio()
    print(background_file)
    # final_meditation = mix_audio(speech_file, background_file)
    # response = requests.get(image)
    # with open("cover_image.png", "wb") as f:
    #     f.write(response.content)
        
    # print("Cover image saved as cover_image.png")
    # return (f"Final meditation saved as {final_meditation}")



def generate_cover_image(user_prompt):
    client = OpenAI(api_key = API_KEY)
    prompt =  f""" Generate a visually appealing cover image for a meditation audio that aligns with the user's current emotional state. 
    Here is how the user is feeling: {user_prompt} NO TEXT AT ALL NO TEXT AT ALL NO TEXT AT ALL 
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    return response.data[0].url

if __name__ == "__main__":
    person_feeling = "The user is currently experiencing significant stress and feelings of being overwhelmed due to lack of preparation for an upcoming mathematics mock exam. Their emotional state reflects uncertainty and imbalance, likely exacerbated by the pressure and anxiety associated with the impending assessment. This emotional turbulence has marked their mood throughout the day, manifesting mainly as stress and sadness."
    user_prompt = f"Generate a meditation script. Here is how the person is feeling: {person_feeling}"
    print(create_meditation(user_prompt, person_feeling))
    # play(AudioSegment.from_file("final_meditation.mp3"))






