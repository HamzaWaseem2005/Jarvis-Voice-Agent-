import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from AGENT.agent import run_agent

print("Speech Recognition engine initialized!")

def speak_text(text):
    print(f"Jarvis (Speaking): {text}")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Speech Error: {e}")

def record_audio(duration=5, samplerate=16000):
    print(f"\nListening... (Speak for {duration} seconds)")
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("Recording complete. Processing with Google...")
    
    filename = "temp_audio.wav"
    sf.write(filename, audio, samplerate)
    return filename

def transcribe_with_google(audio_file_path="temp_audio.wav"):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="en-US")
            return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google service; {e}")
        return ""

if __name__ == "__main__":
    print("\nJarvis React Agent is active! Start speaking (Press Ctrl+C to exit):")
    while True:
        audio_file = record_audio(duration=5)
        
        user_text = transcribe_with_google(audio_file)

        print(f"You said: {user_text}")

        if user_text:
            print("Jarvis is thinking...")
            try:
                reply = run_agent(user_text, user_id="hamza", thread_id="voice_session_4")
                print(f"Jarvis: {reply}")
                speak_text(reply)
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                print(error_msg)
                speak_text(error_msg)
        else:
            print("No speech detected or could not understand, trying again...")