"""Text-to-Speech — speaks text out loud using the local TTS engine."""

import pyttsx3


def speak(text: str) -> None:
    # A fresh engine per call, not a cached/reused one — pyttsx3's Windows
    # SAPI5 driver is unreliable across repeated say()/runAndWait() cycles
    # on the same engine instance (audio gets clipped or silently dropped).
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()
