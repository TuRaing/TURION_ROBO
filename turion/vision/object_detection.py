"""Object detection — runs YOLO on a camera frame and returns what it
found, as structured data (not text) so the Decision Layer (Claude) can
reason about it later, same as STT output does for audio.

Local, free, CPU-only (no GPU on this laptop yet) — uses the "nano" YOLOv8
model, the smallest/fastest variant, since it needs to run per-frame on a
no-GPU machine rather than a one-off call like Claude's API.
"""

from dataclasses import dataclass

import cv2
import numpy as np
from ultralytics import YOLO

_ROTATIONS = (None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE)

MODEL_NAME = "yolov8n.pt"  # nano — smallest/fastest, best fit for CPU-only inference
CONFIDENCE_THRESHOLD = 0.5

_model: YOLO | None = None


@dataclass
class Detection:
    label: str
    confidence: float
    box: tuple[int, int, int, int]  # (x1, y1, x2, y2) pixels


def preload() -> None:
    """Load the YOLO model now instead of on first use (downloads the
    weights on first run, then loads from disk) — call at startup so the
    delay doesn't land mid-conversation, same pattern as the other
    preload() functions (STT/TTS/wake-word)."""
    global _model
    if _model is None:
        _model = YOLO(MODEL_NAME)


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
