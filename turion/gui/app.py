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

from turion.activation import PRESENCE_GREETING_PROMPT, wait_for_activation
from turion.audio.mic_input import record_until_silence
from turion.audio.transcribe_indic import preload as preload_stt
from turion.audio.transcribe_indic import transcribe_indic
from turion.brain.claude_client import is_configured, think
from turion.conversation_log import log_turn
from turion.vision.face_detection import preload as preload_face_detection
from turion.vision.scene_context import get_scene_context
from turion.voice_output.speak import preload as preload_tts
from turion.voice_output.speak import speak
from turion.wake_word.listen import preload as preload_wake_word

_SCENE_JOIN_TIMEOUT = 2.0  # extra seconds to wait for the scene thread after STT finishes,
# beyond that just proceed without camera context this turn rather than stall the reply

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
    preload_face_detection()

    while True:
        _status("listening", "ऐकत आहे...", '"Hi Sisu" म्हणा किंवा कॅमेऱ्यासमोर या')
        source, scene = wait_for_activation()

        if source == "presence":
            _status("active", "व्यक्ती दिसली", "बोलत आहे...")
            greeting = think(PRESENCE_GREETING_PROMPT, scene=scene)
            _add_message("sisu", greeting)
            log_turn("(presence trigger)", greeting)
            speak(greeting)
            scene_thread = None
        else:
            # Kick off the camera glance now, in parallel with recording/STT
            # below -- by the time think() needs it, this is usually already
            # done, so the ~2-4s face-recognition cost is hidden rather than
            # added on top of the turn (see scene_context.py for why this
            # can't just run inside think() itself).
            scene_result: dict = {}
            scene_thread = threading.Thread(target=lambda: scene_result.update(value=get_scene_context()), daemon=True)
            scene_thread.start()

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

        if scene_thread is not None:
            scene_thread.join(timeout=_SCENE_JOIN_TIMEOUT)
            scene = scene_result.get("value")

        _status("active", "विचार करत आहे...")
        try:
            reply = think(text, scene=scene)
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
