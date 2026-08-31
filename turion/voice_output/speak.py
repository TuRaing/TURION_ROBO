"""Text-to-Speech — speaks text out loud.

Routes by script: Devanagari text uses a local Piper voice (pyttsx3's
English SAPI5 voices can't speak Devanagari at all); everything else
(English) uses pyttsx3.

Marathi and Hindi share the Devanagari script, so which of the two a
piece of text "is" can't be reliably auto-detected from the text alone
(an open NLP problem, not specific to TURION). Devanagari defaults to
Marathi (the builder's primary language) — pass lang="hi" explicitly
when the text is known to be Hindi.
"""

import io
import re
import wave

import numpy as np
import pyttsx3
import sounddevice as sd
from huggingface_hub import hf_hub_download
from piper import PiperVoice
from piper.config import SynthesisConfig

PIPER_VOICE_REPO = "rhasspy/piper-voices"
PIPER_VOICES = {
    "mr": {"file": "mr/mr_IN/google/medium/mr_IN-google-medium.onnx", "speaker_id": 8},
    "hi": {"file": "hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx", "speaker_id": None},
}

DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")

_piper_voices: dict[str, PiperVoice] = {}


def _is_devanagari(text: str) -> bool:
    return bool(DEVANAGARI_RE.search(text))


def _get_piper_voice(lang: str) -> PiperVoice:
    if lang not in _piper_voices:
        voice_file = PIPER_VOICES[lang]["file"]
        onnx_path = hf_hub_download(PIPER_VOICE_REPO, voice_file)
        hf_hub_download(PIPER_VOICE_REPO, voice_file + ".json")  # config, loaded alongside
        _piper_voices[lang] = PiperVoice.load(onnx_path)
    return _piper_voices[lang]


def _speak_piper(text: str, lang: str) -> None:
    voice = _get_piper_voice(lang)
    syn_config = SynthesisConfig(speaker_id=PIPER_VOICES[lang]["speaker_id"])
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


def _speak_english(text: str) -> None:
    # A fresh engine per call, not a cached/reused one — pyttsx3's Windows
    # SAPI5 driver is unreliable across repeated say()/runAndWait() cycles
    # on the same engine instance (audio gets clipped or silently dropped).
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def preload(lang: str = "mr") -> None:
    """Load a Piper voice now instead of on first use (~5s) — call at
    startup so the delay doesn't land mid-conversation."""
    _get_piper_voice(lang)


def _split_by_script(text: str) -> list[str]:
    """Group consecutive words into same-script chunks, so a sentence mixing
    Devanagari and English (e.g. "मी TURION आहे") gets each part spoken by
    the right voice instead of the whole thing going through one."""
    chunks: list[str] = []
    for word in text.split():
        is_deva = _is_devanagari(word)
        if chunks and _is_devanagari(chunks[-1].split()[-1]) == is_deva:
            chunks[-1] += " " + word
        else:
            chunks.append(word)
    return chunks


def speak(text: str, lang: str | None = None) -> None:
    """Speak `text`. `lang`: "mr" or "hi" forces that voice for the whole
    text; otherwise each word is routed by script (Devanagari -> Marathi,
    else English) so mixed-language sentences sound right."""
    if lang is not None:
        if lang in PIPER_VOICES:
            _speak_piper(text, lang)
        else:
            _speak_english(text)
        return

    for chunk in _split_by_script(text):
        if _is_devanagari(chunk):
            _speak_piper(chunk, "mr")
        else:
            _speak_english(chunk)
