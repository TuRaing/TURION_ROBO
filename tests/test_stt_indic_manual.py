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

    print("Transcribing (RNNT decoding — usually more accurate than CTC, a bit slower)...")
    text = transcribe_indic(audio, lang="mr", decoding="rnnt")

    print(f"You said: {text}")

    # PowerShell's console font often can't render Devanagari (shows boxes) —
    # write to a file too so it can be read properly.
    with open("tests/last_transcription.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("(also saved to tests/last_transcription.txt for reliable viewing)")
