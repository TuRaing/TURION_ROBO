# TURION — main entry point
# Phase 1 loop: listen -> transcribe -> think -> speak

import sys

import anthropic
import sounddevice as sd

from turion.audio.mic_input import record_until_silence
from turion.audio.transcribe import transcribe
from turion.brain.claude_client import get_client, think
from turion.voice_output.speak import speak


def main():
    try:
        get_client()  # fail fast if ANTHROPIC_API_KEY is missing
    except RuntimeError as e:
        print(f"Cannot start: {e}")
        print('Set your key first: setx ANTHROPIC_API_KEY "your-key-here" (then open a new terminal)')
        sys.exit(1)

    print("TURION Phase 1 — press Enter, then speak. Recording stops automatically when you pause. Ctrl+C to quit.")
    while True:
        input("\nPress Enter to talk...")

        print("Listening...")
        try:
            audio = record_until_silence()
        except sd.PortAudioError as e:
            print(f"Mic error: {e}. Check that a microphone is connected and try again.")
            continue

        print("Transcribing...")
        text = transcribe(audio)
        if not text:
            print("(heard nothing, try again)")
            continue
        print(f"You said: {text}")

        print("Thinking...")
        try:
            reply = think(text)
        except anthropic.APIError as e:
            print(f"Claude API error: {e}. Try again in a moment.")
            continue
        print(f"TURION: {reply}")

        speak(reply)


if __name__ == "__main__":
    main()
