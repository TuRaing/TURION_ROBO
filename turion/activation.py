"""Combines TURION's two ways of starting a conversation turn — the "Hi
Sisu" wake word and camera-based presence detection — into one call that
races them and returns whichever fired first.

Lives at the top level (not under wake_word/ or vision/) because it bridges
both: wake_word/listen.py knows nothing about the camera, vision/presence.py
knows nothing about the mic, and neither should have to.
"""

import threading

from turion.vision.presence import wait_for_presence
from turion.wake_word.listen import wait_for_wake_word

# Synthetic "user_text" fed to claude_client.think() on a presence-triggered
# turn, where nobody has actually said anything yet -- Claude still gets the
# scene text alongside this, so its existing known/unknown scene_line logic
# (see claude_client.think()) naturally produces the right proactive opener:
# addressing a known person by name, or asking an unknown one's name in Hindi.
PRESENCE_GREETING_PROMPT = (
    "(वापरकर्ता अजून काहीच बोललेला नाही — कॅमेऱ्याने आत्ताच एक व्यक्ती जवळ आल्याचं टिपलं आहे. "
    "आधी स्वतःहून एक छोटं वाक्य बोलून त्यांचं लक्ष वेधून घे.)"
)


def wait_for_activation() -> tuple[str, str | None]:
    """Block until either the wake word is heard or a person is seen by the
    camera, whichever comes first, then cancel the other side. Returns
    (source, scene_text): source is "wakeword" or "presence"; scene_text is
    the camera's scene line when source is "presence" (used to seed Sisu's
    proactive greeting), else None (a wake-word turn fetches its own scene
    separately, see main.py/gui/app.py's scene_thread)."""
    stop_event = threading.Event()
    result: dict = {}
    lock = threading.Lock()

    def _finish(source: str, scene_text: str | None = None) -> None:
        with lock:
            if "source" not in result:
                result["source"] = source
                result["scene_text"] = scene_text
                stop_event.set()

    def _watch_wake_word() -> None:
        if wait_for_wake_word(stop_event):
            _finish("wakeword")

    def _watch_presence() -> None:
        scene_text = wait_for_presence(stop_event)
        if scene_text:
            _finish("presence", scene_text)

    t1 = threading.Thread(target=_watch_wake_word, daemon=True)
    t2 = threading.Thread(target=_watch_presence, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    return result["source"], result.get("scene_text")
