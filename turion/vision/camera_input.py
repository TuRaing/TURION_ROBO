"""Camera capture — reads frames from a phone running the "IP Webcam"
Android app over local WiFi, not the laptop's built-in webcam (phone gives
1920x1080 vs. 1280x720, and needs no extra hardware purchase — see
Doc/project_info.md, Phase 2 section, for the full comparison).

Reads the phone's address from the TURION_CAMERA_URL environment variable,
e.g.:
    setx TURION_CAMERA_URL "http://192.168.1.2:8080"
(the address shown in the IP Webcam app after tapping "Start server" —
phone and this computer must be on the same WiFi network).

Polls the /shot.jpg snapshot endpoint rather than opening the /video MJPEG
stream with cv2.VideoCapture — that failed on OpenCV's FFmpeg backend even
though the phone was confirmed reachable (a raw TCP test to the same
host:port succeeded). /shot.jpg works reliably and is a fine way to get
frame-by-frame images for detection.
"""

import os
import urllib.request

import cv2
import numpy as np

_ENV_VAR = "TURION_CAMERA_URL"

# The phone's frames come out rotated by however it's currently being
# held -- confirmed inconsistent across shots in testing (upright, 90-,
# and 180-rotated frames all seen from the same phone), and the IP Webcam
# app has no orientation-lock setting to fix this at the source. So no
# fixed rotation is applied here; turion.vision.object_detection's
# detect_auto_orient() instead tries all 4 rotations per frame and keeps
# whichever one YOLO is confident about. Revisit this once the phone is
# permanently mounted in one fixed position -- a known fixed rotation set
# here would then be cheaper than checking all 4 on every frame.


def _shot_url() -> str:
    base = os.environ.get(_ENV_VAR)
    if not base:
        raise RuntimeError(
            f'{_ENV_VAR} is not set. Open the "IP Webcam" app on the phone, tap "Start server", '
            f'then run: setx {_ENV_VAR} "http://<address shown in the app>" (restart the terminal after).'
        )
    return base.rstrip("/") + "/shot.jpg"


def get_frame(timeout: float = 5.0) -> np.ndarray | None:
    """Fetch the current camera frame as a BGR numpy array (OpenCV's usual
    format), or None if the phone isn't reachable right now (wrong WiFi,
    app not running/screen locked, etc.) — never raises for a transient
    connection failure, since callers should treat a missed frame as
    "try again next loop", not a crash."""
    try:
        data = urllib.request.urlopen(_shot_url(), timeout=timeout).read()
    except OSError:
        return None
    return cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)


def preload() -> bool:
    """Check the camera is reachable now, so a bad TURION_CAMERA_URL or an
    unreachable phone surfaces at startup rather than mid-use. Returns
    True if a frame was successfully fetched."""
    return get_frame() is not None
