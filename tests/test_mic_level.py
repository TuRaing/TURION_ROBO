"""Diagnostic — records audio and reports its volume level (no Whisper).
Helps confirm whether the mic is actually capturing sound.

Run: .venv\\Scripts\\python.exe -m tests.test_mic_level
"""

import numpy as np

from turion.audio.mic_input import record

if __name__ == "__main__":
    input("Press Enter, then speak loudly for 5 seconds...")
    print("Listening...")
    audio = record(5)
    peak = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio ** 2))
    print(f"Peak level: {peak:.4f}  (0 = silence, 1 = max)")
    print(f"RMS level:  {rms:.4f}")
    if peak < 0.01:
        print("=> Looks like SILENCE was captured. Mic may be muted, wrong device, or blocked by Windows privacy settings.")
    else:
        print("=> Mic is capturing real audio.")
