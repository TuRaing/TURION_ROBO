"""TURION desktop app — same listen -> transcribe -> think -> speak loop as
turion/main.py, but running behind a small always-on window (turion/gui/
index.html) instead of a terminal. Models load once at startup and the
window then stays open, continuously listening for "Hi Sisu" — no repeated
reloads between turns.
"""

import threading
from pathlib import Path

import anthropic
import sounddevice as sd
import webview

from turion.audio.mic_input import record_until_silence
from turion.audio.transcribe_indic import preload as preload_stt
from turion.audio.transcribe_indic import transcribe_indic
from turion.brain.claude_client import is_configured, think
from turion.conversation_log import log_turn
from turion.voice_output.speak import preload as preload_tts
from turion.voice_output.speak import speak
from turion.wake_word.listen import preload as preload_wake_word
from turion.wake_word.listen import wait_for_wake_word

HTML_PATH = Path(__file__).parent / "index.html"

_window: webview.Window | None = None


def _status(mode: str, label: str, sub: str = "") -> None:
    if _window is None:
        return
    js = (
        f"window.turion.setStatus({mode!r}, {label!r}, {sub!r})"
        if mode else f"window.turion.setStatus(null, {label!r}, {sub!r})"
    )
    _window.evaluate_js(js)


def _add_message(who: str, text: str) -> None:
    if _window is None:
        return
    _window.evaluate_js(f"window.turion.addMessage({who!r}, {text!r})")


def _assistant_loop() -> None:
    _status(None, "मॉडेल्स load होत आहेत...", "~40 सेकंद, एकदाच")
    preload_stt()
    preload_tts()
    preload_wake_word()

    while True:
        _status("listening", "ऐकत आहे...", '"Hi Sisu" म्हणा')
        wait_for_wake_word()

        _status("active", "ऐकत आहे", "बोला...")
        try:
            audio = record_until_silence()
        except sd.PortAudioError:
            _status("listening", "Mic त्रुटी", "मायक्रोफोन तपासा")
            continue

        _status("active", "समजून घेत आहे...")
        text = transcribe_indic(audio, lang="mr")
        if not text:
            continue
        _add_message("user", text)

        _status("active", "विचार करत आहे...")
        try:
            reply = think(text)
        except anthropic.APIError as e:
            _add_message("sisu", f"त्रुटी: {e}")
            continue
        _add_message("sisu", reply)
        log_turn(text, reply)

        _status("active", "बोलत आहे...")
        speak(reply)


def main() -> None:
    global _window
    if not is_configured():
        print("No ANTHROPIC_API_KEY set — running in STUB mode.")

    _window = webview.create_window(
        "TURION", url=HTML_PATH.as_uri(), width=380, height=640, resizable=True, min_size=(320, 480)
    )
    threading.Thread(target=_assistant_loop, daemon=True).start()
    webview.start(debug=True)


if __name__ == "__main__":
    main()
