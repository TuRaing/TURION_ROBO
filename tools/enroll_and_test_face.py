"""Enroll a person's face (3 angles) and test recognition — NOT part of
the app, a one-off script to try turion/vision/face_recognition_db.py
against the real phone camera. Run it, follow the prompts (front, then
turn left, then turn right), then take one more test photo to see if it
gets recognized.
"""

from turion.vision.camera_input import get_frame
from turion.vision.face_detection import detect_faces_auto_orient
from turion.vision.face_recognition_db import ANGLES, enroll, recognize


def _capture_one_face(prompt: str):
    input(f"\n{prompt} Press Enter when ready...")
    frame = get_frame()
    if frame is None:
        print("Could not fetch a frame from the phone camera. Is the IP Webcam server running?")
        return None
    faces, _ = detect_faces_auto_orient(frame)
    if not faces:
        print("No face found in that frame -- try again, closer/better lit.")
        return None
    if len(faces) > 1:
        print(f"Found {len(faces)} faces -- using the most confident one.")
    return max(faces, key=lambda f: f.confidence)


def main() -> None:
    name = input("Name to enroll: ").strip()
    if not name:
        print("No name given, stopping.")
        return

    prompts = {
        "front": "Look straight at the phone.",
        "left": "Turn your head to show your LEFT profile (~45 degrees).",
        "right": "Turn your head to show your RIGHT profile (~45 degrees).",
    }
    for angle in ANGLES:
        face = _capture_one_face(prompts[angle])
        if face is None:
            print(f"Skipping '{angle}' -- retry the script if you want it enrolled.")
            continue
        enroll(name, face.embedding)
        print(f"Enrolled '{angle}' for {name} (confidence {face.confidence:.2f}).")

    print(f"\nDone enrolling {name}. Now let's test recognition.")
    face = _capture_one_face("Point the phone at a face to recognize (any angle).")
    if face is None:
        return
    result = recognize(face.embedding)
    if result:
        matched_name, score = result
        print(f"Recognized: {matched_name} (similarity {score:.3f})")
    else:
        print("Not recognized (no match above threshold).")


if __name__ == "__main__":
    main()
