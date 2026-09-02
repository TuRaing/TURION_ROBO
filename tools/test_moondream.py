"""Moondream comparison test — NOT part of the app. Moondream2 is a tiny
(2B) vision-language model that runs on CPU, unlike Claude's vision API --
free, local, no internet needed, but slower per-call than YOLO. Testing
whether it can describe/name the thermos/flask-shaped black bottle that
both plain YOLOv8n and YOLO-World missed.
"""

import cv2
from PIL import Image
from transformers import AutoModelForCausalLM

from turion.vision.camera_input import get_frame

MODEL_NAME = "vikhyatk/moondream2"
MODEL_REVISION = "2025-06-21"


def main() -> None:
    frame = get_frame()
    if frame is None:
        print("Could not fetch a frame from the phone camera. Is the IP Webcam server running?")
        return

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    print(f"Loading {MODEL_NAME} (downloads on first run, ~2B params)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, revision=MODEL_REVISION, trust_remote_code=True, device_map={"": "cpu"}
    )

    print("\n--- Caption ---")
    print(model.caption(image, length="normal")["caption"])

    print("\n--- Query: what objects are on the desk/shelf? ---")
    print(model.query(image, "List every distinct object you can see, one per line.")["answer"])

    print("\n--- Query: the black bottle specifically ---")
    print(model.query(image, "What is the black cylindrical object on the shelf?")["answer"])


if __name__ == "__main__":
    main()
