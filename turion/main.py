# TURION — main entry point
# Phase 1 loop: listen -> transcribe -> think -> speak

from turion.audio.mic_input import record_until_silence
from turion.audio.transcribe import transcribe
from turion.brain.claude_client import think
from turion.voice_output.speak import speak


def main():
    print("TURION Phase 1 — press Enter, then speak. Recording stops automatically when you pause. Ctrl+C to quit.")
    while True:
        input("\nPress Enter to talk...")

        print("Listening...")
        audio = record_until_silence()

        print("Transcribing...")
        text = transcribe(audio)
        if not text:
            print("(heard nothing, try again)")
            continue
        print(f"You said: {text}")

        print("Thinking...")
        reply = think(text)
        print(f"TURION: {reply}")

        speak(reply)


if __name__ == "__main__":
    main()
