"""Hindu festival dates — computed from real Panchanga (tithi) data rather
than hardcoded, so it works for any year without manual updates.

jyotishganit doesn't expose the lunar month (masa) directly, so festivals
are found by searching for their tithi within the Gregorian-calendar month
window that festival is known to fall in (these windows are wide enough to
always contain the real date, even though the exact date shifts year to
year with the lunar calendar).
"""

from datetime import datetime, timedelta

from jyotishganit.components.panchanga import create_panchanga
from jyotishganit.core.astronomical import calculate_ayanamsa, get_timescale

# (festival name, target tithi, search window as (month, day) start/end —
# end month/day can wrap past Dec 31 into the next year, handled below)
_FESTIVALS = [
    ("गणेश चतुर्थी", "Shukla Chaturthi", (8, 10), (9, 20)),
    ("श्रीकृष्ण जन्माष्टमी", "Krishna Ashtami", (7, 25), (9, 5)),
    ("रक्षाबंधन", "Purnima", (7, 10), (8, 25)),
    ("नवरात्रारंभ", "Shukla Pratipada", (9, 1), (10, 10)),
    ("दसरा", "Shukla Dashami", (9, 10), (10, 20)),
    ("दिवाळी (लक्ष्मीपूजन)", "Amavasya", (10, 10), (11, 20)),
    ("होळी", "Purnima", (2, 10), (3, 25)),
    ("गुढीपाडवा", "Shukla Pratipada", (3, 10), (4, 20)),
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
