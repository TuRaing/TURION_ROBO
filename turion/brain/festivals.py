"""Hindu festival dates — computed from real Panchanga (tithi) data rather
than hardcoded, so it works for any year without manual updates.

jyotishganit doesn't expose the lunar month (masa) directly, so festivals
are found by searching for their tithi within a Gregorian-calendar window
narrow enough (<29.5 days, one lunar cycle) to contain only the single real
occurrence — a wider window risks matching the *previous* month's instance
of the same tithi instead. Verified against real published 2026 dates.
"""

from datetime import date, datetime, timedelta

from skyfield import almanac
from skyfield.api import wgs84

from jyotishganit.components.panchanga import create_panchanga
from jyotishganit.core.astronomical import calculate_ayanamsa, get_ephemeris, get_timescale

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
_observer = wgs84.latlon(_LAT, _LON)


def _sunrise_datetime(d: date) -> datetime:
    """Actual computed sunrise (IST) for date `d` at the reference location.
    Traditional panchanga assigns a calendar day the tithi active at its
    *real* sunrise, which shifts through the year — not a fixed clock hour.
    Tried fixed 6 AM and noon proxies first; both produced wrong-day results
    for at least one festival (see git history), because the real
    sunrise-tithi boundary doesn't line up with either fixed guess. This is
    the astronomically correct version, not another approximation."""
    ts = get_timescale()
    eph = get_ephemeris()
    t0 = ts.utc(d.year, d.month, d.day)
    t1 = ts.utc(d.year, d.month, d.day + 1)
    f = almanac.sunrise_sunset(eph, _observer)
    times, events = almanac.find_discrete(t0, t1, f)
    sunrise_t = times[list(events).index(1)]  # event == 1 is sunrise
    utc_dt = sunrise_t.utc_datetime().replace(tzinfo=None)
    return utc_dt + timedelta(hours=_TZ_OFFSET)


def _tithi_at(dt: datetime) -> str:
    utc_dt = dt - timedelta(hours=_TZ_OFFSET)
    ts = get_timescale()
    t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second)
    ayanamsa = calculate_ayanamsa(t)
    return create_panchanga(dt, _TZ_OFFSET, ayanamsa).tithi


def _tithi_on(d: date, target_tithis: set) -> bool:
    """True if `d` shows one of `target_tithis` at sunrise, OR at 9 AM/3 PM/
    9 PM local — a tithi can be short enough to start and end within one day
    without ever coinciding with sunrise ("tithi kshaya", confirmed
    happening for real in March 2026 — see git history), which would
    otherwise make it invisible to a sunrise-only check. Not a full
    traditional kshaya-tithi resolution rule, just a pragmatic net."""
    if _tithi_at(_sunrise_datetime(d)) in target_tithis:
        return True
    return any(_tithi_at(datetime(d.year, d.month, d.day, h, 0, 0)) in target_tithis for h in (9, 15, 21))


def _find_festival_date(target_tithi: str, start_md: tuple, end_md: tuple, year: int) -> date | None:
    """Search day-by-day for the first date whose tithi matches, within the
    given (month, day) window."""
    start = date(year, *start_md)
    end_year = year + 1 if end_md < start_md else year
    end = date(end_year, *end_md)
    day = start
    while day <= end:
        if _tithi_on(day, {target_tithi}):
            return day
        day += timedelta(days=1)
    return None


def get_upcoming_festivals(count: int = 3) -> str:
    """Returns a short Marathi-labeled summary of the next `count` upcoming
    festivals, as a string ready to drop into the system prompt. Computed
    once per calendar year and cached (full-year scan takes only a few
    seconds thanks to jyotishganit's direct panchanga API)."""
    today = date.today()
    if _cache["year"] != today.year:
        results = []
        for name, tithi, start_md, end_md in _FESTIVALS:
            found = _find_festival_date(tithi, start_md, end_md, today.year)
            if found is None:
                # tried this year's window and missed (e.g. already passed) — try next year
                found = _find_festival_date(tithi, start_md, end_md, today.year + 1)
            if found:
                results.append((found, name))
        results.sort()
        _cache["festivals"] = results
        _cache["year"] = today.year

    upcoming = [(d, n) for d, n in _cache["festivals"] if d >= today]
    if not upcoming:
        return "कुठलाही आगामी सण सापडला नाही."
    lines = [f"{n}: {d.strftime('%d %B %Y')}" for d, n in upcoming[:count]]
    return "; ".join(lines)


def _find_next(target_tithis: set, from_date: date, max_days: int = 35) -> date | None:
    """Search forward from `from_date` for the next date whose tithi is in
    `target_tithis`. Used for recurring (monthly/twice-monthly) fasting
    observances (Ekadashi, Sankashti) rather than once-a-year festivals —
    no window needed, just "the next one from today"."""
    day = from_date
    for _ in range(max_days):
        if _tithi_on(day, target_tithis):
            return day
        day += timedelta(days=1)
    return None


def get_next_ekadashi_sankashti() -> str:
    """Ekadashi (11th tithi, twice a month) and Sankashti Chaturthi (Krishna
    Chaturthi, once a month) recur too often to list a full year — just the
    next occurrence of each from today, computed fresh each call (each
    search is only ~1-15 days out, so this is fast — no caching needed).
    These are fasting/vrat days, so getting the date right matters more
    than for a general festival — hence the sunrise-based calculation."""
    today = date.today()
    ekadashi = _find_next({"Shukla Ekadashi", "Krishna Ekadashi"}, today)
    sankashti = _find_next({"Krishna Chaturthi"}, today)
    parts = []
    if ekadashi:
        parts.append(f"पुढची एकादशी: {ekadashi.strftime('%d %B %Y')}")
    if sankashti:
        parts.append(f"पुढची संकष्टी चतुर्थी: {sankashti.strftime('%d %B %Y')}")
    return "; ".join(parts) if parts else "गणना करता आली नाही."
