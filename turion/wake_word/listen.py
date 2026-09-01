"""Wake-word detection — listens continuously on the mic and returns once
the trigger phrase ("Hi Sisu") is heard, so TURION can stay always-on
instead of needing "press Enter to talk" for every turn.

Custom model trained via openWakeWord (github.com/dscripka/openWakeWord),
see Doc/project_info.md for the full training story.
"""

from pathlib import Path

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from turion.audio.mic_input import SAMPLE_RATE

WAKE_WORD_MODEL_PATH = str(Path(__file__).parent / "models" / "hi_si_su.onnx")
WAKE_WORD_NAME = "hi_si_su"
DETECTION_THRESHOLD = 0.5
CHUNK_SAMPLES = 1280  # ~80ms at 16kHz — openWakeWord's expected chunk size

_model = None


def _get_model() -> Model:
    global _model
    if _model is None:
        _model = Model(wakeword_models=[WAKE_WORD_MODEL_PATH], inference_framework="onnx")
    return _model


def preload() -> None:
    """Load the wake-word model now instead of on first use — call at
    startup so the delay doesn't land mid-conversation."""
    _get_model()


def wait_for_wake_word() -> None:
    """Block, listening continuously, until "Hi Sisu" is heard."""
    model = _get_model()
    model.reset()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
        while True:
            block, _ = stream.read(CHUNK_SAMPLES)
            prediction = model.predict(block.flatten())
            if prediction[WAKE_WORD_NAME] > DETECTION_THRESHOLD:
                return
