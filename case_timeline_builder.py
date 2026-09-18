#!/usr/bin/env python3
"""
case_timeline_builder.py
Converts raw case event notes into a formatted chronological timeline.
Accepts either a JSON file of structured events, or a plain .txt file of
free-text note lines in the same flexible shorthand the web tool accepts
(e.g. "8/28 6:41pm - password reset via self-service").

Live demo: https://biancabcarlson.github.io/Case-Timeline-Builder/

Usage:
    python case_timeline_builder.py notes.json --gap-hours 72 -o timeline.md
    python case_timeline_builder.py notes.txt --case-year 2026 -o timeline.md

Input format (notes.json) — SYNTHETIC EXAMPLE:
[
  {"date": "2026-08-28T18:41", "note": "Password reset requested via self-service portal."},
  {"date": "2026-08-30T00:18", "note": "Two-factor method changed from SMS to email."},
  {"date": "2026-08-30T00:24", "note": "Login succeeded from a foreign IP shortly after the 2FA change."},
  {"date": "2026-08-31T09:40", "note": "New external payee added to account."},
  {"date": "2026-08-31T10:15", "note": "Outbound withdrawal request submitted to the new payee."}
]

Input format (notes.txt) — SYNTHETIC EXAMPLE, one raw note per line:
8/28 6:41pm - password reset via self-service
8/30 12:18am - two-factor method changed from SMS to email
Aug 31, 2026 9:40am: new external payee added to account
"""

import json
import re
import argparse
from datetime import datetime

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

ISO_RE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[T ](\d{1,2}):(\d{2})(?::\d{2})?)?")
SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?(?:[ ,]+(\d{1,2})(?::(\d{2}))?\s*([ap]\.?m\.?)?)?", re.I)
MONTH_RE = re.compile(
    r"^([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})?(?:[ ,]+(\d{1,2})(?::(\d{2}))?\s*([ap]\.?m\.?)?)?",
    re.I,
)
SEP_RE = re.compile(r"^[\s\-–—:|,.]+")


def _two_digit_year(y):
    y = int(y)
    return 2000 + y if y < 70 else (1900 + y if y < 100 else y)


def _to_24h(h, ampm):
    h = int(h)
    if not ampm:
        return h
    is_pm = ampm.lower().startswith("p")
    if h == 12:
        return 12 if is_pm else 0
    return h + 12 if is_pm else h


def parse_line(line, default_year):
    """Mirrors the parseLine() logic in index.html. Returns (dt, time_unknown, note) or None."""
    m = ISO_RE.match(line)
    if m:
        y, mo, d, h, mi = m.groups()
        time_unknown = h is None
        dt = datetime(int(y), int(mo), int(d), int(h) if h else 0, int(mi) if mi else 0)
        rest = SEP_RE.sub("", line[m.end():])
        return dt, time_unknown, rest

    m = SLASH_RE.match(line)
    if m:
        mo, d, y, h, mi, ampm = m.groups()
        year = _two_digit_year(y) if y else default_year
        time_unknown = h is None
        hour = _to_24h(h, ampm) if h else 0
        dt = datetime(year, int(mo), int(d), hour, int(mi) if mi else 0)
        rest = SEP_RE.sub("", line[m.end():])
        return dt, time_unknown, rest

    m = MONTH_RE.match(line)
    if m:
        mon_str, d, y, h, mi, ampm = m.groups()
        key4, key3 = mon_str[:4].lower(), mon_str[:3].lower()
        key = key4 if key4 in MONTHS else key3
        if key not in MONTHS:
            return None
        year = int(y) if y else default_year
        time_unknown = h is None
        hour = _to_24h(h, ampm) if h else 0
        dt = datetime(year, MONTHS[key], int(d), hour, int(mi) if mi else 0)
        rest = SEP_RE.sub("", line[m.end():])
        return dt, time_unknown, rest

    return None


def load_events_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    events = []
    for e in data:
        date_value = e["date"]
        time_value = e.get("time")
        time_unknown = bool(e.get("time_unknown", e.get("timeSpecified") is False))
        if time_value and not time_unknown and "T" not in date_value and " " not in date_value:
            date_value = f"{date_value}T{time_value}"
        dt = datetime.fromisoformat(date_value)
        events.append({
            "dt": dt,
            "time_unknown": time_unknown,
            "note": e["note"].strip(),
            "type": e.get("type", "Event"),
            "source": e.get("source", ""),
        })
    return events


def load_events_txt(path, default_year):
    events = []
    skipped = []
    with open(path, "r") as f:
        for i, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            parsed = parse_line(line, default_year)
            if not parsed or not parsed[2]:
                skipped.append((i, line))
                continue
            dt, time_unknown, note = parsed
            events.append({
                "dt": dt,
                "time_unknown": time_unknown,
                "note": note,
                "type": "Investigator note",
                "source": "Text import",
            })
    if skipped:
        for i, line in skipped:
            print(f"Warning: line {i} could not be parsed and was skipped: {line!r}")
    return events


def build_timeline(events, gap_hours):
    events = sorted(events, key=lambda x: x["dt"])
    lines = ["# Case Timeline", ""]
    prev = None
    for i, e in enumerate(events, start=1):
        stamp = e["dt"].strftime("%Y-%m-%d") if e["time_unknown"] else e["dt"].strftime("%Y-%m-%d %H:%M")
        suffix = " (time not specified)" if e["time_unknown"] else ""
        source = f" · {e['source']}" if e.get("source") else ""
        event_type = f" [{e['type']}]" if e.get("type") else ""
        lines.append(f"**{i}. {stamp}{suffix}**{event_type}{source} — {e['note']}")
        if prev:
            gap = (e["dt"] - prev).total_seconds() / 3600
            if gap >= gap_hours:
                approx = " (approximate — one entry has no time, just a date)" if e["time_unknown"] else ""
                lines.append(f"   > ⚠️ Gap of {round(gap)} hours since previous entry — verify nothing missing.{approx}")
        lines.append("")
        prev = e["dt"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Build a chronological case timeline from raw notes (JSON or free-text .txt).")
    ap.add_argument("input", help="Path to a JSON file of structured events, or a .txt file of free-text note lines")
    ap.add_argument("--gap-hours", type=float, default=48.0,
                     help="Flag gaps between entries larger than this many hours (default: 48)")
    ap.add_argument("--case-year", type=int, default=datetime.now().year,
                     help="Default year to assume for .txt lines that don't include one (default: current year)")
    ap.add_argument("-o", "--output", default="timeline.md", help="Output Markdown file")
    args = ap.parse_args()

    if args.input.lower().endswith(".json"):
        events = load_events_json(args.input)
    else:
        events = load_events_txt(args.input, args.case_year)

    timeline_md = build_timeline(events, args.gap_hours)

    with open(args.output, "w") as f:
        f.write(timeline_md)

    print(f"Timeline written to {args.output} ({len(events)} events)")


if __name__ == "__main__":
    main()
