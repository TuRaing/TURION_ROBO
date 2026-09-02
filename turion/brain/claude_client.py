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
import re
from datetime import datetime

import anthropic

MODEL = "claude-haiku-4-5-20251001"  # cheap model for early testing

# Piper tries to sound out emoji characters instead of skipping them, producing
# garbled audio — Claude doesn't reliably follow the "no emoji" instruction
# (small/cheap model), so strip them here as a backstop before speak() ever sees them.
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # symbols, pictographs, emoticons, transport, supplemental
    "\U00002600-\U000027BF"  # misc symbols, dingbats (includes folded hands 🙏 range's neighbors)
    "\U0001F1E6-\U0001F1FF"  # regional indicators (flags)
    "\U00002190-\U000021FF"  # arrows
    "\U0000FE0F"             # variation selector-16 (emoji presentation)
    "]+",
    flags=re.UNICODE,
)

SYSTEM_PROMPT = (
    "You are Sisu, a helpful voice assistant (TURION is the name of the overall project/robot "
    "you're part of, but introduce yourself as Sisu in conversation). Keep replies short and "
    "conversational — "
    "this is a spoken interface, not a chat window, so avoid long explanations, lists, or emoji. "
    "Reply in Marathi by default. If the user's message is clearly in Hindi or English instead, "
    "reply in that same language. If the transcribed text is too short, garbled, or unclear to "
    "understand, say so briefly in Marathi and ask them to repeat — do not guess or give a generic "
    "greeting. This reply will be spoken aloud by a Marathi-only voice, so when writing in "
    "Devanagari script, spell out any English words/names phonetically in Devanagari too (e.g. "
    "'वेबसाइट', 'गूगल') instead of switching to Latin script mid-sentence — Latin-script text gets "
    "badly mispronounced by the voice engine. Avoid naming specific external websites/apps by "
    "their Latin-script name; describe the action instead (e.g. 'तुमच्या फोनवरील हवामान अ‍ॅप' rather "
    "than naming a specific app)."
)

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
        return f'[STUB] ऐकलं: "{user_text}"'

    client = get_client()
    today = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    system = f"{SYSTEM_PROMPT}\n\nToday's date and time: {today}."
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": user_text}],
    )
    reply = response.content[0].text
    reply = _EMOJI_RE.sub("", reply)
    return re.sub(r"[ \t]+", " ", reply).strip()
