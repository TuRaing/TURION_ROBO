"""Decision layer — sends transcribed text to Claude and returns a reply.

Reads the API key from the ANTHROPIC_API_KEY environment variable.
Set it yourself before running (do not hardcode it in code):
    setx ANTHROPIC_API_KEY "your-key-here"

If no key is set, think() returns a stub reply instead of calling the API —
lets the rest of the pipeline (mic -> STT -> here -> TTS) be tested for
free before real API credit is available. Swapping in a real key later
needs no code changes.
"""

import os

import anthropic

MODEL = "claude-haiku-4-5-20251001"  # cheap model for early testing

SYSTEM_PROMPT = "You are TURION, a helpful voice assistant. Keep replies short and conversational."

_client = None


def is_configured() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def get_client() -> anthropic.Anthropic:
    """Create (or reuse) the Anthropic client. Raises RuntimeError if
    ANTHROPIC_API_KEY isn't set."""
    global _client
    if _client is None:
        if not is_configured():
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set.")
        _client = anthropic.Anthropic()
    return _client


def think(user_text: str) -> str:
    """Send user_text to Claude and return the reply text. Returns a stub
    reply instead if ANTHROPIC_API_KEY isn't set."""
    if not is_configured():
        return f"[STUB — no API key set] You said: \"{user_text}\". This is a placeholder reply."

    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
    )
    return response.content[0].text
