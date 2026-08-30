"""Manual test — mic input + Whisper transcription only. No Claude API, no TTS.

Run: python -m tests.test_stt_manual
"""

import numpy as np

from turion.audio.mic_input import record_until_silence
from turion.audio.transcribe import transcribe

if __name__ == "__main__":
    input("Press Enter, wait half a second quietly, then speak (recording stops automatically after you pause)...")
    print("Listening...")
    audio = record_until_silence()

    peak = np.max(np.abs(audio))
    print(f"(debug) peak level: {peak:.4f}  duration: {len(audio) / 16000:.1f}s")

    print("Transcribing...")
    text = transcribe(audio, debug=True)

    print(f"You said: {text}")
