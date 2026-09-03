"""Decision layer — sends transcribed text to Claude and returns a reply.

Reads the API key from the ANTHROPIC_API_KEY environment variable.
Set it yourself before running (do not hardcode it in code):
    setx ANTHROPIC_API_KEY "your-key-here"

If no key is set, think() returns a stub reply instead of calling the API —
lets the rest of the pipeline (mic -> STT -> here -> TTS) be tested for
free before real API credit is available. Swapping in a real key later
needs no code changes.
"""

import base64
import os
import re
from datetime import datetime

import anthropic
import cv2
from jyotishganit import calculate_birth_chart

from turion.brain.festivals import get_next_ekadashi_sankashti, get_upcoming_festivals
from turion.vision.camera_input import get_frame

# Reference location for panchanga (tithi/nakshatra) calculation — Pune,
# Maharashtra, since the builder is a Marathi speaker. Panchanga varies
# slightly by location (sunrise-based day boundaries), so this is an
# approximation; fine for conversational use.
_PANCHANGA_LAT = 18.52
_PANCHANGA_LON = 73.85

_panchanga_cache: dict = {"date": None, "text": None}

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
    "you're part of, but introduce yourself as Sisu in conversation). This is a spoken interface, "
    "not a chat window: keep replies to 1-2 short sentences by default — every extra sentence is "
    "extra time spent speaking aloud. Only go longer than that if the user explicitly asks for "
    "detail or a list of things. Avoid long explanations, filler phrases, or emoji. "
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

# Lets Claude ask for a real image description on demand (e.g. "हे काय आहे?")
# instead of only ever having YOLO-style labels. Deliberately NOT called
# every turn -- Claude decides when it's actually needed, which keeps the
# extra vision-API cost (~1600+200 tokens, see project_info.md) to only the
# turns that genuinely ask about something visible.
TOOLS = [
    {
        "name": "describe_camera_view",
        "description": (
            "Get a detailed description of what the camera currently sees. Use this only when the "
            "user explicitly asks what something is, asks for a description of an object/scene, or "
            "otherwise clearly needs more visual detail than you already have -- not on every turn."
        ),
        "input_schema": {"type": "object", "properties": {}},
    }
]

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


def _get_panchanga_text() -> str:
    """Today's Hindu Panchanga (tithi/nakshatra/etc.), cached per calendar day
    since the calculation is slow (~seconds) and doesn't need to run every turn."""
    today_date = datetime.now().date()
    if _panchanga_cache["date"] != today_date:
        chart = calculate_birth_chart(
            birth_date=datetime.now(),
            latitude=_PANCHANGA_LAT,
            longitude=_PANCHANGA_LON,
            timezone_offset=5.5,
        )
        p = chart.panchanga
        _panchanga_cache["text"] = (
            f"तिथी {p.tithi}, नक्षत्र {p.nakshatra}, योग {p.yoga}, करण {p.karana}, वार {p.vaara}"
        )
        _panchanga_cache["date"] = today_date
    return _panchanga_cache["text"]


def _describe_camera_view() -> str:
    """Fetch a fresh frame (the scene-context one may be stale/gone by now)
    and get a real natural-language description from Claude's vision --
    this is the actual image-analysis call, unlike the cheap local
    face-recognition glance in scene_context.py. Used only as a tool
    result, on-demand, per TOOLS above."""
    frame = get_frame(timeout=3.0)
    if frame is None:
        return "कॅमेरा सध्या उपलब्ध नाही (फोन दिसत नाहीये)."
    ok, buf = cv2.imencode(".jpg", frame)
    image_b64 = base64.b64encode(buf.tobytes()).decode("ascii")
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                    {"type": "text", "text": "Briefly describe what's visible in this image, in Marathi."},
                ],
            }
        ],
    )
    return _extract_text(response)


def _extract_text(response) -> str:
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


def think(user_text: str, scene: str | None = None) -> str:
    """Send user_text to Claude and return the reply text. Returns a stub
    reply instead if ANTHROPIC_API_KEY isn't set.

    `scene`: optional camera-context string from
    turion.vision.scene_context.get_scene_context(), e.g. "समोर Tushar
    दिसत आहे". Fetching it is the caller's job, not this function's --
    callers that care about latency (the live voice loop) should fetch it
    in a background thread parallel to STT rather than block here; this
    function just uses whatever it's given, including None (no camera)."""
    if not is_configured():
        return f'[STUB] ऐकलं: "{user_text}"'

    client = get_client()
    today = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    panchanga = _get_panchanga_text()
    festivals = get_upcoming_festivals()
    ekadashi_sankashti = get_next_ekadashi_sankashti()
    if scene and "अनोळखी" in scene:
        scene_line = (
            f"RIGHT NOW: {scene}. You don't know this person yet. Before anything else, in Hindi, ask "
            f"their name and/or which language they'd prefer to talk in (e.g. 'आपका नाम क्या है?' or "
            f"'आप किस भाषा में बात करना पसंद करेंगे?') — ask in Hindi specifically, not Marathi, since you "
            f"don't yet know what they speak. Once they answer, continue that conversation in "
            f"whichever language they used."
        )
    elif scene:
        scene_line = (
            f"RIGHT NOW: {scene}. You are talking to this known person — address them by that name "
            f"somewhere in your very next reply, naturally (not 'I see you're X', just talk to them "
            f"the way you'd talk to someone you recognize)."
        )
    else:
        scene_line = "RIGHT NOW: no automatic camera glance was available this turn."
    system = (
        f"{SYSTEM_PROMPT}\n\n{scene_line} If the user asks what something is, asks you to describe "
        "what's around them/in front of them, or otherwise clearly wants visual detail beyond what "
        "you already know, use the describe_camera_view tool to actually look — don't guess, and "
        "don't claim you have no camera access without trying the tool first.\n\n"
        f"Today's date and time: {today}. "
        f"Today's Hindu Panchanga (approximate, calculated for Pune): {panchanga}. "
        f"Upcoming major festivals (calculated, not guessed — trust these dates): {festivals}. "
        f"{ekadashi_sankashti}. "
        f"For any festival/vrat date not covered above, say you don't have a calculated date "
        f"for it rather than guessing."
    )
    messages = [{"role": "user", "content": user_text}]
    response = client.messages.create(
        model=MODEL,
        max_tokens=150,  # replies are meant to be 1-2 spoken sentences — caps worst-case latency too
        system=system,
        tools=TOOLS,
        messages=messages,
    )

    if response.stop_reason == "tool_use":
        tool_use = next(b for b in response.content if b.type == "tool_use")
        description = _describe_camera_view()
        messages.append({"role": "assistant", "content": response.content})
        messages.append(
            {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": description}],
            }
        )
        response = client.messages.create(
            model=MODEL,
            max_tokens=150,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

    reply = _extract_text(response)
    reply = _EMOJI_RE.sub("", reply)
    return re.sub(r"[ \t]+", " ", reply).strip()
