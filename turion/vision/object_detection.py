"""Object detection — runs YOLO-World on a camera frame and returns what
it found, as structured data (not text) so the Decision Layer (Claude) can
reason about it later, same as STT output does for audio.

Local, free, CPU-only (no GPU on this laptop yet). Uses YOLO-World
(open-vocabulary — matches any class name given in CLASSES, not limited to
COCO's fixed 80 categories) rather than plain YOLOv8, and specifically the
"medium" size variant — chosen after directly comparing small/medium/
large/extra-large on the same real test photo (a cluttered desk with a
black insulated-flask-shaped bottle that plain YOLOv8n's fixed classes
missed entirely). Medium gave the highest confidence on that bottle (94%)
of ALL four sizes, including the larger, slower, more expensive ones —
extra-large actually did worst (36%). Bigger isn't automatically better
for open-vocabulary detection; this was decided from evidence, not
assumption. Also compared directly against Claude's vision API on the same
photo: Claude never named the black bottle correctly in three attempts,
while medium YOLO-World did, for free and near-instantly (vs. ~1600+200
tokens per call) -- confirms local YOLO-World as the right default for
continuous detection, with Claude vision reserved for when a spoken
conversation actually needs it (see claude_client.py notes / project_info.md).
"""

from dataclasses import dataclass

import cv2
import numpy as np
from ultralytics import YOLO

_ROTATIONS = (None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE)

MODEL_NAME = "yolov8m-worldv2.pt"  # "medium" -- see module docstring for why this size specifically
CONFIDENCE_THRESHOLD = 0.45  # slightly below the usual 0.5 -- real objects (e.g. headphones at 0.499
# in testing) landed just under 0.5 with this open-vocabulary model's confidence calibration

# Household/desk objects TURION is likely to actually be asked about. Not
# exhaustive -- extend this list as new object types come up in practice
# (open-vocabulary detection only finds what it's told to look for).
CLASSES = [
    "laptop", "bottle", "thermos", "flask", "water bottle", "black steel bottle",
    "insulated flask", "medicine bottle", "headphones", "mouse", "keyboard",
    "box", "book", "notebook", "pen", "phone", "cup", "remote",
]

_model: YOLO | None = None


@dataclass
class Detection:
    label: str
    confidence: float
    box: tuple[int, int, int, int]  # (x1, y1, x2, y2) pixels


def preload() -> None:
    """Load the YOLO-World model now instead of on first use (downloads
    the weights on first run, then loads from disk) — call at startup so
    the delay doesn't land mid-conversation, same pattern as the other
    preload() functions (STT/TTS/wake-word)."""
    global _model
    if _model is None:
        _model = YOLO(MODEL_NAME)
        _model.set_classes(CLASSES)


def detect(frame: np.ndarray) -> list[Detection]:
    """Run object detection on one BGR frame (as returned by
    turion.vision.camera_input.get_frame()) and return every detection
    above CONFIDENCE_THRESHOLD."""
    if frame is None:
        # Passing None to YOLO doesn't raise -- ultralytics silently falls
        # back to running on its own bundled demo image instead, which
        # would look like a real (but completely wrong) result. Guard
        # against that explicitly rather than ever letting it happen.
        raise ValueError("detect() got frame=None -- camera_input.get_frame() failed to fetch a frame")
    preload()
    results = _model(frame, verbose=False)[0]
    detections = []
    for box in results.boxes:
        confidence = float(box.conf[0])
        if confidence < CONFIDENCE_THRESHOLD:
            continue
        label = results.names[int(box.cls[0])]
        x1, y1, x2, y2 = (int(v) for v in box.xyxy[0])
        detections.append(Detection(label=label, confidence=confidence, box=(x1, y1, x2, y2)))
    return detections


def detect_auto_orient(frame: np.ndarray) -> tuple[list[Detection], np.ndarray]:
    """Like detect(), but tries the frame at all 4 rotations and keeps
    whichever orientation YOLO is most confident about overall, instead of
    assuming a fixed orientation. Needed because a handheld (or not yet
    permanently mounted) phone camera can send frames at any rotation
    depending on how it's currently held — a single hardcoded rotation
    can't work for that (confirmed: the same phone sent upright, 90-, and
    180-rotated frames across different shots in one test session).

    Returns (detections, the frame rotated to match) since callers often
    want to draw/save a correctly-oriented image too. Costs ~4x the
    compute of detect() -- fine for a phone camera polled at a few fps,
    but prefer detect() with a known-fixed rotation once the camera's
    mount position is fixed (see camera_input.py)."""
    if frame is None:
        raise ValueError("detect_auto_orient() got frame=None -- camera_input.get_frame() failed to fetch a frame")

    best_detections: list[Detection] = []
    best_frame = frame
    best_score = -1.0
    for rotation in _ROTATIONS:
        candidate = cv2.rotate(frame, rotation) if rotation is not None else frame
        detections = detect(candidate)
        score = sum(d.confidence for d in detections)
        if score > best_score:
            best_score = score
            best_detections = detections
            best_frame = candidate
    return best_detections, best_frame
