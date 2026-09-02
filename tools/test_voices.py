"""Piper Marathi voice comparison tool — NOT part of the app, a one-off
listening test to help pick the clearest speaker_id and speaking speed for
turion/voice_output/speak.py. Run it, listen, note which one sounded
clearest, then update PIPER_VOICES["mr"]["speaker_id"] in speak.py by hand.
"""

import io
import wave

import numpy as np
import sounddevice as sd
from huggingface_hub import hf_hub_download
from piper import PiperVoice
from piper.config import SynthesisConfig

VOICE_FILE = "mr/mr_IN/google/medium/mr_IN-google-medium.onnx"
NUM_SPEAKERS = 9  # from the voice's .onnx.json — see num_speakers

TEST_SENTENCE = "नमस्कार! मी सिसू आहे. आज बुधवार, दोन सप्टेंबर आहे, आणि पुढची एकादशी सात सप्टेंबरला आहे."

CURRENT_SPEAKER_ID = 8  # what speak.py uses today, for reference


def _load_voice() -> PiperVoice:
    onnx_path = hf_hub_download("rhasspy/piper-voices", VOICE_FILE)
    hf_hub_download("rhasspy/piper-voices", VOICE_FILE + ".json")
    return PiperVoice.load(onnx_path)


def _play(voice: PiperVoice, text: str, speaker_id: int, length_scale: float | None = None) -> None:
    syn_config = SynthesisConfig(speaker_id=speaker_id, length_scale=length_scale)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        voice.synthesize_wav(text, wf, syn_config=syn_config)
    buf.seek(0)
    with wave.open(buf, "rb") as wf:
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    audio = np.frombuffer(raw, dtype=np.int16)
    sd.play(audio, sr)
    sd.wait()


def main() -> None:
    print("Piper Marathi voice loading...")
    voice = _load_voice()
    print(f'Test sentence: "{TEST_SENTENCE}"\n')

    print("--- Part 1: all 9 speakers (current default is", CURRENT_SPEAKER_ID, ") ---")
    for speaker_id in range(NUM_SPEAKERS):
        input(f"\nPress Enter to hear speaker_id={speaker_id}...")
        _play(voice, f"स्पीकर क्रमांक {speaker_id}.", speaker_id)
        _play(voice, TEST_SENTENCE, speaker_id)

    input(f"\nPress Enter to compare speaking SPEED on speaker_id={CURRENT_SPEAKER_ID}...")
    print("--- Part 2: speaking speed on the current speaker ---")
    for label, length_scale in [("normal (1.0)", 1.0), ("slower (1.15)", 1.15), ("slowest (1.3)", 1.3)]:
        input(f"\nPress Enter to hear {label}...")
        _play(voice, TEST_SENTENCE, CURRENT_SPEAKER_ID, length_scale=length_scale)

    print("\nDone. Whichever speaker_id/length_scale sounded clearest — update speak.py by hand.")


if __name__ == "__main__":
    main()
