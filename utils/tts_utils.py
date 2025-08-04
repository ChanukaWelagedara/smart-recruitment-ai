# utils/tts_utils.py
import pyttsx3

def speak_text(text: str, rate: int = 160, volume: float = 1.0):
  
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.say(text)
    engine.runAndWait()
