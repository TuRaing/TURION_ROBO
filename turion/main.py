# TURION — main entry point
# Phase 1 loop: listen -> transcribe -> think -> speak

import time

import anthropic
import sounddevice as sd

from turion.audio.mic_input import record_until_silence
from turion.audio.transcribe_indic import preload as preload_stt
from turion.audio.transcribe_indic import transcribe_indic
from turion.brain.claude_client import MODEL, is_configured, think
from turion.voice_output.speak import preload as preload_tts
from turion.voice_output.speak import speak


def main():
    if not is_configured():
        print("No ANTHROPIC_API_KEY set — running in STUB mode (fake replies, no cost).")
        print('Set a real key later with: setx ANTHROPIC_API_KEY "your-key-here"')

    print("Loading voice models, please wait (~40 seconds, one-time)...")
    preload_stt()
    preload_tts()

    print("TURION Phase 1 — press Enter, then speak. Recording stops automatically when you pause. Ctrl+C to quit.")
    while True:
        input("\nPress Enter to talk...")

        print("Listening...")
        try:
            audio = record_until_silence()
        except sd.PortAudioError as e:
            print(f"Mic error: {e}. Check that a microphone is connected and try again.")
            continue

        print("Transcribing... (module: IndicConformer, local)")
        t0 = time.time()
        text = transcribe_indic(audio, lang="mr")
        print(f"(debug) transcribe time: {time.time() - t0:.2f}s")
        if not text:
            print("(heard nothing, try again)")
            continue
        print(f"You said: {text}")

        mode = f"Claude API, model: {MODEL}" if is_configured() else "STUB mode, no API call"
        print(f"Thinking... (module: {mode})")
        t0 = time.time()
        try:
            reply = think(text)
        except anthropic.APIError as e:
            print(f"Claude API error: {e}. Try again in a moment.")
            continue
        print(f"(debug) think time: {time.time() - t0:.2f}s")
        print(f"TURION: {reply}")

        print("Speaking...")
        t0 = time.time()
        speak(reply)
        print(f"(debug) speak time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
