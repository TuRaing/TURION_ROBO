"""Hindu festival dates — computed from real Panchanga (tithi) data rather
than hardcoded, so it works for any year without manual updates.

jyotishganit doesn't expose the lunar month (masa) directly, so festivals
are found by searching for their tithi within a Gregorian-calendar window
narrow enough (<29.5 days, one lunar cycle) to contain only the single real
occurrence — a wider window risks matching the *previous* month's instance
of the same tithi instead. Verified against real published 2026 dates.
"""

from datetime import datetime, timedelta

from jyotishganit.components.panchanga import create_panchanga
from jyotishganit.core.astronomical import calculate_ayanamsa, get_timescale

# (festival name, target tithi, search window as (month, day) start/end —
# end month/day can wrap past Dec 31 into the next year, handled below)
#
# IMPORTANT: each window must span LESS than one lunar cycle (~29.5 days).
# A wider window can contain the *same* tithi twice (this month's and next
# month's), and the search below returns whichever it finds first — silently
# picking the wrong occurrence. Confirmed by testing against real published
# 2026 dates: the first version of this list (wider windows) put Ganesh
# Chaturthi, Dussehra, and Diwali a full lunar month too early.
_FESTIVALS = [
    ("गणेश चतुर्थी", "Shukla Chaturthi", (9, 4), (9, 24)),
    ("श्रीकृष्ण जन्माष्टमी", "Krishna Ashtami", (8, 18), (9, 7)),
    ("रक्षाबंधन", "Purnima", (8, 18), (9, 7)),
    ("नवरात्रारंभ", "Shukla Pratipada", (10, 1), (10, 20)),
    ("दसरा", "Shukla Dashami", (10, 10), (10, 30)),
    ("दिवाळी (लक्ष्मीपूजन)", "Amavasya", (10, 29), (11, 18)),
    ("होळी", "Purnima", (2, 21), (3, 13)),
    ("गुढीपाडवा", "Shukla Pratipada", (3, 9), (3, 29)),
]

_TZ_OFFSET = 5.5  # IST
_LAT, _LON = 18.52, 73.85  # Pune — see claude_client.py for the same note

_cache: dict = {"year": None, "festivals": None}


def _panchanga_for(dt: datetime):
    utc_dt = dt - timedelta(hours=_TZ_OFFSET)
    ts = get_timescale()
    t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second)
    ayanamsa = calculate_ayanamsa(t)
    return create_panchanga(dt, _TZ_OFFSET, ayanamsa)


def _find_festival_date(target_tithi: str, start_md: tuple, end_md: tuple, year: int) -> datetime | None:
    """Search day-by-day (checked at noon local time) for the first date
    whose tithi matches, within the given (month, day) window of `year`."""
    start = datetime(year, *start_md, 12, 0, 0)
    end_year = year + 1 if end_md < start_md else year
    end = datetime(end_year, *end_md, 12, 0, 0)
    day = start
    while day <= end:
        if _panchanga_for(day).tithi == target_tithi:
            return day
        day += timedelta(days=1)
    return None


def get_upcoming_festivals(count: int = 3) -> str:
    """Returns a short Marathi-labeled summary of the next `count` upcoming
    festivals, as a string ready to drop into the system prompt. Computed
    once per calendar year and cached (full-year scan takes only a few
    seconds thanks to jyotishganit's direct panchanga API)."""
    today = datetime.now()
    if _cache["year"] != today.year:
        results = []
        for name, tithi, start_md, end_md in _FESTIVALS:
            date = _find_festival_date(tithi, start_md, end_md, today.year)
            if date is None:
                # tried this year's window and missed (e.g. already passed) — try next year
                date = _find_festival_date(tithi, start_md, end_md, today.year + 1)
            if date:
                results.append((date, name))
        results.sort()
        _cache["festivals"] = results
        _cache["year"] = today.year

    upcoming = [(d, n) for d, n in _cache["festivals"] if d.date() >= today.date()]
    if not upcoming:
        return "कुठलाही आगामी सण सापडला नाही."
    lines = [f"{n}: {d.strftime('%d %B %Y')}" for d, n in upcoming[:count]]
    return "; ".join(lines)


def _find_next(target_tithis: set, from_date: datetime, max_days: int = 35) -> datetime | None:
    """Search forward day-by-day from `from_date` for the next date whose
    tithi is in `target_tithis`. Used for recurring (monthly/twice-monthly)
    observances rather than once-a-year festivals — no window needed, just
    "the next one from today"."""
    day = from_date
    for _ in range(max_days):
        if _panchanga_for(day).tithi in target_tithis:
            return day
        day += timedelta(days=1)
    return None


def get_next_ekadashi_sankashti() -> str:
    """Ekadashi (11th tithi, twice a month) and Sankashti Chaturthi (Krishna
    Chaturthi, once a month) recur too often to list a full year — just the
    next occurrence of each from today, computed fresh each call (each
    search is only ~1-15 days out, so this is fast — no caching needed)."""
    today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    ekadashi = _find_next({"Shukla Ekadashi", "Krishna Ekadashi"}, today)
    sankashti = _find_next({"Krishna Chaturthi"}, today)
    parts = []
    if ekadashi:
        parts.append(f"पुढची एकादशी: {ekadashi.strftime('%d %B %Y')}")
    if sankashti:
        parts.append(f"पुढची संकष्टी चतुर्थी: {sankashti.strftime('%d %B %Y')}")
    return "; ".join(parts) if parts else "गणना करता आली नाही."
