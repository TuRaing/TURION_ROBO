"""Face detection — runs InsightFace on a camera frame and returns where
faces are (not who they are yet — matching against known people is
Phase 3/Memory territory, once a local database of known faces exists).

Chosen over `face_recognition` (the other common Python option): that
library depends on `dlib`, which has no official Windows wheels and needs
compiling Boost.Python from source to install on Windows -- exactly the
kind of dependency pain this project has repeatedly hit and avoided
elsewhere (see the wake-word training notes in project_info.md).
InsightFace installed cleanly with no compilation step, and runs on
`onnxruntime`, already a project dependency for wake-word detection.
"""

from dataclasses import dataclass

import cv2
import numpy as np
from insightface.app import FaceAnalysis

MODEL_PACK = "buffalo_l"  # InsightFace's standard accurate model pack
DETECTION_THRESHOLD = 0.5

# Same reasoning as turion.vision.object_detection._ROTATIONS -- the phone
# camera's orientation isn't fixed shot to shot, and face detectors are
# calibrated for upright faces, so a fixed rotation can't be assumed here
# either.
_ROTATIONS = (None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE)

_app: FaceAnalysis | None = None


@dataclass
class Face:
    confidence: float
    box: tuple[int, int, int, int]  # (x1, y1, x2, y2) pixels
    embedding: np.ndarray  # 512-d face embedding, for Phase 3 face matching later


def preload() -> None:
    """Load the InsightFace model now instead of on first use (downloads
    the model pack on first run, then loads from disk) — call at startup
    so the delay doesn't land mid-conversation, same pattern as the other
    preload() functions (STT/TTS/wake-word/object detection)."""
    global _app
    if _app is None:
        _app = FaceAnalysis(name=MODEL_PACK, providers=["CPUExecutionProvider"])
        _app.prepare(ctx_id=-1, det_thresh=DETECTION_THRESHOLD)  # ctx_id=-1 -- CPU only, no GPU on this laptop


def detect_faces(frame: np.ndarray) -> list[Face]:
    """Run face detection on one BGR frame (as returned by
    turion.vision.camera_input.get_frame()) and return every face found."""
    if frame is None:
        raise ValueError("detect_faces() got frame=None -- camera_input.get_frame() failed to fetch a frame")
    preload()
    faces = _app.get(frame)
    return [
        Face(
            confidence=float(f.det_score),
            box=tuple(int(v) for v in f.bbox),
            embedding=f.embedding,
        )
        for f in faces
    ]


def detect_faces_auto_orient(frame: np.ndarray) -> tuple[list[Face], np.ndarray]:
    """Like detect_faces(), but tries the frame at all 4 rotations and
    keeps whichever orientation finds the most/highest-confidence faces --
    see turion.vision.object_detection.detect_auto_orient() for the full
    reasoning (same underlying problem: the phone's orientation isn't
    fixed). Returns (faces, the frame rotated to match)."""
    if frame is None:
        raise ValueError("detect_faces_auto_orient() got frame=None -- camera_input.get_frame() failed to fetch a frame")

    best_faces: list[Face] = []
    best_frame = frame
    best_score = -1.0
    for rotation in _ROTATIONS:
        candidate = cv2.rotate(frame, rotation) if rotation is not None else frame
        faces = detect_faces(candidate)
        score = sum(f.confidence for f in faces)
        if score > best_score:
            best_score = score
            best_faces = faces
            best_frame = candidate
    return best_faces, best_frame
