# utils/tts_utils.py
import pyttsx3

def speak_text(text: str, rate: int = 160, volume: float = 1.0):
    """
    Convert the given text to speech using pyttsx3.

    Args:
        text (str): The text to be spoken.
        rate (int): Speaking rate (default: 160).
        volume (float): Volume level from 0.0 to 1.0 (default: 1.0).
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.say(text)
    engine.runAndWait()
