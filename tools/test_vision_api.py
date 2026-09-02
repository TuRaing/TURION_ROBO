"""Claude vision comparison test — NOT part of the app, a one-off check of
how Claude's vision (multimodal) compares to local YOLO for object
recognition, since YOLO is limited to its 80 trained COCO classes and
missed a thermos-shaped bottle that didn't match its "bottle" prototype
closely enough. Sends one frame from the phone camera to Claude and asks
for a full list of what it sees.

Costs real API tokens per call, unlike YOLO (free, local) — this is meant
to inform a design decision (when is it worth calling Claude vision vs.
relying on local YOLO alone), not to become the default per-frame path.
"""

import base64
import os

import anthropic
import cv2

from turion.vision.camera_input import get_frame

MODEL = "claude-haiku-4-5-20251001"


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set.")
        return

    frame = get_frame()
    if frame is None:
        print("Could not fetch a frame from the phone camera. Is the IP Webcam server running?")
        return

    ok, buf = cv2.imencode(".jpg", frame)
    image_b64 = base64.b64encode(buf.tobytes()).decode("ascii")

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
                    },
                    {
                        "type": "text",
                        "text": "List every distinct object you can see in this image, one per line.",
                    },
                ],
            }
        ],
    )
    print(response.content[0].text)
    print(f"\n(tokens used: input={response.usage.input_tokens}, output={response.usage.output_tokens})")


if __name__ == "__main__":
    main()
