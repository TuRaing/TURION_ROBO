"""Manual test — TTS output only. No mic, no Claude API.

Run: python -m tests.test_tts_manual
"""

from turion.voice_output.speak import speak

if __name__ == "__main__":
    print("Speaking now — listen for it...")
    speak("Hello, this is TURION. Can you hear me clearly?")
    print("Done. Did you hear that clearly?")
