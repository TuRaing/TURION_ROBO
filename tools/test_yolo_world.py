"""YOLO-World visual test — NOT part of the app, a way to try any
YOLO-World size against a live phone frame and see the drawn boxes.
Open-vocabulary detection (part of the same `ultralytics` package already
installed) -- unlike plain YOLOv8n, it isn't limited to 80 fixed COCO
classes; you give it a list of things to look for in plain text.

Comparing small/medium/large/extra-large on a real test photo (a
cluttered desk with a black insulated-flask-shaped bottle) found medium
gave the highest confidence on that bottle (94%) of all four sizes --
bigger was not better here, extra-large did worst (36%). That's why
turion/vision/object_detection.py (the actual production module) uses
"m", the same default as here -- edit MODEL_NAME below to try a different
size against a fresh frame.
"""

import cv2
from ultralytics import YOLO

from turion.vision.camera_input import get_frame

MODEL_NAME = "yolov8m-worldv2.pt"  # "medium" -- see module docstring for why
CUSTOM_CLASSES = [
    "laptop", "bottle", "thermos", "flask", "water bottle", "black steel bottle",
    "insulated flask", "medicine bottle", "headphones", "mouse", "keyboard",
    "box", "book", "notebook", "pen", "phone", "cup", "remote",
]


def main() -> None:
    frame = get_frame()
    if frame is None:
        print("Could not fetch a frame from the phone camera. Is the IP Webcam server running?")
        return

    print(f"Loading {MODEL_NAME} (downloads on first run)...")
    model = YOLO(MODEL_NAME)
    model.set_classes(CUSTOM_CLASSES)

    results = model(frame, verbose=False)[0]
    print(f"Classes searched for: {CUSTOM_CLASSES}\n")
    print("Detections:")
    for box in results.boxes:
        conf = float(box.conf[0])
        label = results.names[int(box.cls[0])]
        print(f" - {label}: {conf:.3f}")
        x1, y1, x2, y2 = (int(v) for v in box.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(frame, f"{label} {conf:.2f}", (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imwrite("yolo_world_result.jpg", frame)
    print("\nSaved yolo_world_result.jpg")


if __name__ == "__main__":
    main()
