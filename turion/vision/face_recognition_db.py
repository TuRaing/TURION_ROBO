"""Named face recognition — remembers whose face is whose, on top of
turion.vision.face_detection's plain "is there a face here" detection.

Stores each known person as MULTIPLE embeddings (one per enrolled angle --
front, left three-quarter, right three-quarter) rather than just one,
because a single frontal-only embedding fails to recognize the same
person from an angle. This is the realistic, achievable target -- a full
90-degree side profile is genuinely hard for any 2D face recognition
system (a whole eye and half the face go missing), not just this one, so
it isn't attempted here. Matching a NEW face against ALL of a person's
stored angle-embeddings (not just one) and taking the best match is what
makes recognition work across front-to-~45-degree angles.

Storage is a local JSON file, NOT committed to git (see .gitignore) --
face embeddings are personal biometric data tied to a real identity, same
privacy reasoning as why logs/ (conversation history) is excluded.
"""

import json
from pathlib import Path

import numpy as np

DB_PATH = Path(__file__).parent.parent.parent / "data" / "known_faces.json"
MATCH_THRESHOLD = 0.4  # cosine similarity above this counts as a match -- see recognize()

ANGLES = ("front", "left", "right")  # the 3 angles enrollment asks for -- see module docstring


def _load() -> dict[str, list[list[float]]]:
    if not DB_PATH.exists():
        return {}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def _save(db: dict[str, list[list[float]]]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(db), encoding="utf-8")


def enroll(name: str, embedding: np.ndarray) -> None:
    """Add one angle's embedding for `name`. Call once per angle (see
    ANGLES) — the more angles enrolled, the more angles recognize() can
    later match against."""
    db = _load()
    db.setdefault(name, []).append(embedding.tolist())
    _save(db)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def recognize(embedding: np.ndarray) -> tuple[str, float] | None:
    """Compare `embedding` against every stored angle of every known
    person and return (best matching name, similarity score) if the best
    match clears MATCH_THRESHOLD, else None (unknown person) -- an
    "I don't recognize this person" result is preferred over a confident
    wrong guess."""
    db = _load()
    best_name = None
    best_score = -1.0
    for name, embeddings in db.items():
        for stored in embeddings:
            score = _cosine_similarity(embedding, np.array(stored))
            if score > best_score:
                best_score = score
                best_name = name
    if best_name is not None and best_score >= MATCH_THRESHOLD:
        return best_name, best_score
    return None


def known_names() -> list[str]:
    return list(_load().keys())
