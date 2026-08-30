"""Manual test — mic input + IndicConformer transcription (Marathi). No Claude API, no TTS.

Run: python -m tests.test_stt_indic_manual
"""

import numpy as np

from turion.audio.mic_input import record_until_silence
from turion.audio.transcribe_indic import transcribe_indic

if __name__ == "__main__":
    input("Press Enter, wait half a second quietly, then speak in Marathi...")
    print("Listening...")
    audio = record_until_silence()

    peak = np.max(np.abs(audio))
    print(f"(debug) peak level: {peak:.4f}  duration: {len(audio) / 16000:.1f}s")

    print("Transcribing (first run downloads the model, may take a few minutes)...")
    text = transcribe_indic(audio, lang="mr")

    print(f"You said: {text}")
