"""Text-to-Speech — speaks text out loud.

Default voice is Marathi Piper for everything, including English words
mixed into a reply (see `speak()` for why). `lang="hi"` uses the Hindi
Piper voice instead; `lang="en"` uses pyttsx3.
"""

import io
import wave

import numpy as np
import pyttsx3
import sounddevice as sd
from huggingface_hub import hf_hub_download
from piper import PiperVoice
from piper.config import SynthesisConfig

PIPER_VOICE_REPO = "rhasspy/piper-voices"
PIPER_VOICES = {
    "mr": {"file": "mr/mr_IN/google/medium/mr_IN-google-medium.onnx", "speaker_id": 5},
    "hi": {"file": "hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx", "speaker_id": None},
}

_piper_voices: dict[str, PiperVoice] = {}


def _get_piper_voice(lang: str) -> PiperVoice:
    if lang not in _piper_voices:
        voice_file = PIPER_VOICES[lang]["file"]
        onnx_path = hf_hub_download(PIPER_VOICE_REPO, voice_file)
        hf_hub_download(PIPER_VOICE_REPO, voice_file + ".json")  # config, loaded alongside
        _piper_voices[lang] = PiperVoice.load(onnx_path)
    return _piper_voices[lang]


def _speak_piper(text: str, lang: str) -> None:
    print(f"  (module) TTS: Piper [{lang}] -> \"{text}\"")
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
    print(f"  (module) TTS: pyttsx3 [en] -> \"{text}\"")
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


def speak(text: str, lang: str = "mr") -> None:
    """Speak `text` entirely in one voice (default Marathi Piper) — no
    per-word script-splitting. Splitting sounded worse in practice: each
    switch between engines is a separate audio clip, so consecutive
    English/Devanagari chunks played back with audible gaps between them,
    and alternating the (male) pyttsx3 English voice into a (female) Piper
    Marathi reply mid-sentence was jarring. One consistent voice for the
    whole reply — English words spoken with a Marathi accent — sounds
    smoother overall than a technically-correct but choppy, voice-switching
    readout. `lang`: "mr" or "hi" (Piper) or "en" (pyttsx3)."""
    if lang in PIPER_VOICES:
        _speak_piper(text, lang)
    else:
        _speak_english(text)
