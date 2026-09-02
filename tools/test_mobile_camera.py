"""Mobile-camera-as-webcam test — NOT part of the app, a one-off check that
a phone running the "IP Webcam" Android app can be read as a video source
over local WiFi, as a higher-quality alternative to the laptop's own
webcam (confirmed: phone gives 1920x1080, laptop caps at 1280x720).

Uses the /shot.jpg snapshot endpoint polled in a loop, not /video — the
MJPEG stream endpoint failed to open via cv2.VideoCapture's FFmpeg backend
(network/port were confirmed reachable via a raw TCP test, so it's an
OpenCV stream-parsing issue, not a connectivity one); polling snapshots is
simpler and reliable, and is a fine way to get "continuous video" for
frame-by-frame detection anyway.

Usage: edit PHONE_URL below to the address shown in the IP Webcam app
(e.g. "http://192.168.1.2:8080"), then run this script. Shows a live
window; press 'q' to quit, 's' to save the current frame as a JPEG.
"""

import urllib.request

import cv2
import numpy as np

PHONE_URL = "http://192.168.1.2:8080"  # <-- edit to match the IP Webcam app screen
SHOT_URL = PHONE_URL.rstrip("/") + "/shot.jpg"


def _fetch_frame() -> np.ndarray | None:
    try:
        data = urllib.request.urlopen(SHOT_URL, timeout=5).read()
    except OSError:
        return None
    return cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)


def main() -> None:
    print(f"Fetching from {SHOT_URL} ...")
    frame = _fetch_frame()
    if frame is None:
        print("Could not reach the phone. Check: same WiFi, server running on phone, URL correct.")
        return
    print(f"Connected. Frame size: {frame.shape[1]}x{frame.shape[0]}")
    print("Press 'q' to quit, 's' to save a snapshot.")

    while True:
        frame = _fetch_frame()
        if frame is None:
            print("Lost connection.")
            break
        cv2.imshow("Mobile Camera Test", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            cv2.imwrite("mobile_camera_snapshot.jpg", frame)
            print("Saved mobile_camera_snapshot.jpg")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
