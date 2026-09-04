"""Presence-triggered listening — lets a person who walks up to the camera
skip the "Hi Sisu" wake word entirely, instead of needing to know to say it.

Polls the camera in the background while TURION is otherwise idle waiting
for the wake word (see turion.activation, which races this against
turion.wake_word.listen.wait_for_wake_word). Any face — known or unknown —
counts; the known-vs-unknown handling itself already lives in
turion.brain.claude_client.think() via the scene text this returns.

Per-person cooldown stops the same person standing in frame from
re-triggering every poll — keyed by recognized name, or a single shared key
for "some unknown person" (an unknown person's identity can't be tracked
across polls without re-running recognition against nothing, so this is a
deliberate simplification, not per-unknown-individual).
"""

import threading
import time

from turion.vision.scene_context import get_scene_state

POLL_INTERVAL = 4.0  # seconds between camera checks while idle -- InsightFace's 4-rotation
# check isn't free on this CPU-only laptop (see face_detection.py), and this runs
# continuously alongside the always-on wake-word listener, so don't poll too eagerly.
# Revisit once the camera is on a fixed mount and rotation-checking gets cheaper.
COOLDOWN_SECONDS = 120  # don't re-trigger for the same person again within this window

_UNKNOWN_KEY = "__unknown__"

_last_triggered: dict[str, float] = {}


def wait_for_presence(stop_event: threading.Event) -> str | None:
    """Poll the camera until a cooldown-eligible face is seen, or until
    stop_event is set by someone else (e.g. the wake word fired first).
    Returns the scene text (same format as
    turion.vision.scene_context.get_scene_context()) to seed the proactive
    greeting, or None if cancelled via stop_event before any face
    qualified."""
    while not stop_event.is_set():
        state = get_scene_state()
        if state:
            name, scene_text = state
            key = name or _UNKNOWN_KEY
            now = time.time()
            if now - _last_triggered.get(key, 0.0) >= COOLDOWN_SECONDS:
                _last_triggered[key] = now
                return scene_text
        stop_event.wait(POLL_INTERVAL)
    return None
