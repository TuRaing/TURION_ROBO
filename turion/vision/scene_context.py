"""Scene context — syncs vision with the voice loop. Captures who the
phone camera currently sees and formats it as a short Marathi-labeled
string ready to drop into Sisu's system prompt, same pattern as
turion.brain.festivals's date/festival text.

Face recognition only, not object detection -- measured live at ~8.7s for
both together with the phone still handheld (needs a 4-rotation check per
detector, see face_detection.py/object_detection.py), too slow to add to
every voice turn. Face-only roughly halves that. The caller is expected
to also run this in a background thread parallel to STT (see gui/app.py)
to hide most of the remaining latency behind time that's already being
spent recording/transcribing — this module itself stays synchronous and
simple, not threaded, so it's usable standalone (e.g. from a script) too.

Must never break voice: if the camera isn't reachable (phone off, wrong
WiFi, etc.), returns None quickly rather than raising or stalling the
conversation — voice already works standalone and camera is a bonus on
top of it, not a dependency.
"""

from turion.vision.camera_input import get_frame
from turion.vision.face_detection import detect_faces_auto_orient
from turion.vision.face_recognition_db import recognize

_CAMERA_TIMEOUT = 2.0  # short -- don't stall a voice turn waiting on an unreachable phone


def get_scene_context() -> str | None:
    """One-line summary of who the camera currently sees, or None if the
    camera isn't reachable right now (or anything else in the vision
    pipeline fails) — deliberately broad error handling here, since the
    module contract is that vision must never break a voice turn."""
    try:
        frame = get_frame(timeout=_CAMERA_TIMEOUT)
        if frame is None:
            return None

        faces, _ = detect_faces_auto_orient(frame)
        if not faces:
            return None

        best = max(faces, key=lambda f: f.confidence)
        result = recognize(best.embedding)
        if result:
            name, _ = result
            return f"समोर {name} दिसत आहे"
        return "समोर एक अनोळखी व्यक्ती दिसत आहे"
    except Exception:
        return None
