"""Conversation logging — appends each turn to a local JSONL file for later
review (and as raw material if the builder wants to fine-tune/refine
TURION's behavior from real usage later)."""

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "logs" / "conversations.jsonl"


def log_turn(user_text: str, assistant_text: str) -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user_text,
        "assistant": assistant_text,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
