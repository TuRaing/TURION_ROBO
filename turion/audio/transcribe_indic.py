"""Speech-to-Text for Marathi/Indic languages — AI4Bharat IndicConformer (local, free).

Better accuracy than generic Whisper for Marathi, at a similar model size.
Note: loading this model runs custom code from the Hugging Face repo
(`trust_remote_code=True`) — standard for this model family, from a
well-known open research org (AI4Bharat, IIT Madras), but worth knowing.
"""

import numpy as np
import torch
from transformers import AutoModel

MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = AutoModel.from_pretrained(MODEL_ID, trust_remote_code=True)
    return _model


def transcribe_indic(audio: np.ndarray, lang: str = "mr", decoding: str = "ctc") -> str:
    """Transcribe a float32 mono audio array (16kHz) to text for an Indian language.

    lang: ISO code, e.g. "mr" (Marathi), "hi" (Hindi).
    decoding: "ctc" (faster) or "rnnt" (usually more accurate, slower).
    """
    if len(audio) == 0:
        return ""
    model = _get_model()
    wav = torch.from_numpy(audio).unsqueeze(0)  # shape (1, samples), already 16kHz mono
    result = model(wav, lang, decoding)
    return result if isinstance(result, str) else str(result)
