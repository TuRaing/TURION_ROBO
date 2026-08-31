"""Decision layer — sends transcribed text to Claude and returns a reply.

Reads the API key from the ANTHROPIC_API_KEY environment variable.
Set it yourself before running (do not hardcode it in code):
    setx ANTHROPIC_API_KEY "your-key-here"
"""

import os

import anthropic

MODEL = "claude-haiku-4-5-20251001"  # cheap model for early testing

SYSTEM_PROMPT = "You are TURION, a helpful voice assistant. Keep replies short and conversational."

_client = None


def get_client() -> anthropic.Anthropic:
    """Create (or reuse) the Anthropic client. Raises RuntimeError immediately
    if ANTHROPIC_API_KEY isn't set — call this early to fail fast (the SDK
    itself only fails once you make an actual API call, which is too late)."""
    global _client
    if _client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set.")
        _client = anthropic.Anthropic()
    return _client


def think(user_text: str) -> str:
    """Send user_text to Claude and return the reply text."""
    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
    )
    return response.content[0].text
