# Required Libraries, .env Variables, and API Keys
import os
from dotenv import load_dotenv
import json
import openai
from elevenlabs import set_api_key, generate, save
from prompt_engineering import SYSTEM_PROMPT
from backend_clinic_info import backend_clinic_info

# Load .env variables
load_dotenv()

# Set API Keys
openai.api_key = os.getenv("OPENAI_API_KEY")
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

# Set scenario folder paths
SCENARIO_DIR = "02_audio/second_scenario"
INPUT_DIR = os.path.join(SCENARIO_DIR, "input")
OUTPUT_DIR = os.path.join(SCENARIO_DIR, "output")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Transcribe Audio (Speech-to-Text)
def transcribe_audio(file_path): 
    audio_file = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

# Synthesize Assistant Response (Text-to-Speech)
def synthesize_speech(text, output_path):
    audio = generate(
        text=text,
        voice="Sarah",  
        model="eleven_monolingual_v1"
    )
    save(audio, output_path)

# Core Assistant Loop
def run_assistant():
    print("🩺 Voice AI Assistant is running...\n")

    backend_context = json.dumps(backend_clinic_info, indent=2)

    # Initialize chat history
    chat_history = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}\n\nHere is the clinic backend data you can reference:\n{backend_context}"
        }
    ]

    # Initial greeting
    greeting = "Hello! You've reached Chamber Cardiology Clinic. I am an AI assistant — how can I help you today?"
    print(f"Assistant: {greeting}")
    synthesize_speech(greeting, os.path.join(OUTPUT_DIR, "ai_response_0.mp3"))
    os.system(f"afplay {os.path.join(OUTPUT_DIR, 'ai_response_0.mp3')}")
    chat_history.append({"role": "assistant", "content": greeting})

    input_number = 1

    while True:
        audio_input_path = os.path.join(INPUT_DIR, f"user_input_{input_number}.mp3")
        audio_output_path = os.path.join(OUTPUT_DIR, f"ai_response_{input_number}.mp3")

        print(f"\n Waiting for: {audio_input_path}")
        input(" Drop your file and press Enter to continue...")

        if not os.path.exists(audio_input_path):
            print(" No input audio file found. Try again.")
            continue

        # Transcribe user input
        user_input = transcribe_audio(audio_input_path)
        print(f"User: {user_input}")
        chat_history.append({"role": "user", "content": user_input})
      #  Play user's voice input aloud (simulate a real call)
        os.system(f"afplay {audio_input_path}")

        # Generate AI response
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=chat_history
        )
        assistant_response = response["choices"][0]["message"]["content"]
        print(f"Assistant: {assistant_response}")
        chat_history.append({"role": "assistant", "content": assistant_response})

        # Synthesize and save
        synthesize_speech(assistant_response, audio_output_path)
        os.system(f"afplay {audio_output_path}")
        print(f" Saved assistant response to: {audio_output_path}")

# Always increment input number for next turn
        input_number += 1

# Run it
if __name__ == "__main__":
    run_assistant()

    
 