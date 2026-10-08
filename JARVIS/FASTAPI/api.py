from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import speech_recognition as sr
import os
import pyttsx3
from AGENT.agent import run_agent

app = FastAPI()

GLOBAL_THREAD_ID = "hamza_permanent_thread"
GLOBAL_USER_ID = "hamza"

def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Speech Error: {e}")

class TextChatRequest(BaseModel):
    message: str

@app.post("/chat/text")
def chat_with_text(request: TextChatRequest):
    response = run_agent(
        request.message, 
        user_id=GLOBAL_USER_ID, 
        thread_id=GLOBAL_THREAD_ID
    )
    speak_text(response)
    return {
        "thread_id": GLOBAL_THREAD_ID,
        "response": response
    }

@app.post("/chat/voice")
async def chat_with_voice(file: UploadFile = File(...)):
    temp_audio_path = f"temp_{file.filename}"
    with open(temp_audio_path, "wb") as buffer:
        buffer.write(await file.read())
        
    r = sr.Recognizer()
    user_message = ""
    try:
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = r.record(source)
            user_message = r.recognize_google(audio_data, language="en-US")
    except:
        user_message = ""
        
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
        
    if not user_message:
        return {"error": "Audio samajh nahi aayi."}
        
    response = run_agent(
        user_message, 
        user_id=GLOBAL_USER_ID, 
        thread_id=GLOBAL_THREAD_ID
    )
    speak_text(response)
    
    return {
        "transcribed_text": user_message,
        "thread_id": GLOBAL_THREAD_ID,
        "response": response
    }