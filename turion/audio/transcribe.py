"""Speech-to-Text — wraps local Whisper model."""

import numpy as np
import whisper

from turion.audio.mic_input import SAMPLE_RATE

_model = None

LANGUAGE = None  # auto-detect — user may speak English or Marathi
SILENCE_THRESHOLD = 0.02  # amplitude below this is treated as silence
PADDING_SECONDS = 0.3  # keep a little silence around detected speech


def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("small")
    return _model


def _trim_silence(audio: np.ndarray) -> np.ndarray:
    """Cut leading/trailing silence so Whisper doesn't hallucinate over dead air."""
    loud = np.where(np.abs(audio) > SILENCE_THRESHOLD)[0]
    if len(loud) == 0:
        return audio[:0]  # nothing but silence
    pad = int(PADDING_SECONDS * SAMPLE_RATE)
    start = max(0, loud[0] - pad)
    end = min(len(audio), loud[-1] + pad)
    return audio[start:end]


def transcribe(audio: np.ndarray, debug: bool = False) -> str:
    """Transcribe a float32 mono audio array (16kHz) to text."""
    audio = _trim_silence(audio)
    if len(audio) < SAMPLE_RATE * 0.3:  # too short to contain real speech
        return ""

    model = _get_model()
    result = model.transcribe(
        audio,
        fp16=False,
        language=LANGUAGE,
        initial_prompt="The assistant's name is TURION.",
        condition_on_previous_text=False,
        verbose=True if debug else None,
    )
    if debug:
        print("(debug) trimmed audio length (s):", len(audio) / SAMPLE_RATE)
        print("(debug) detected/used language:", result.get("language"))
        print("(debug) segments:", result.get("segments"))
    return result["text"].strip()
