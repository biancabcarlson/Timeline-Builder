# Timeline Builder

**🔗 Live demo:** https://biancabcarlson.github.io/Timeline-Builder/

Turns raw, unordered investigator notes, account evidence, document findings,
interview notes, and investigator decisions into a numbered, chronological
timeline, and flags unusually large gaps between entries. The browser demo
also receives evidence directly from the other suite tools, so the
investigator does not need to copy and paste rows by hand.

## Cross-tool evidence inbox

On the Simulated Account page, **Add to timeline** is available on account
activity, ACH, crypto, login/IP, and security-review evidence. It opens a
review composer for the event text, date/time, time-known status, and source.
Selecting **Add to timeline** queues the reviewed event in the shared
browser-local inbox. Timeline Builder imports it automatically when opened
and shows the source on the event.

The queue uses `localStorage` under the key
`investigatorSuiteTimelineInbox`; custom timeline events persist under
`investigatorSuiteTimelineEvents`. This is appropriate for the included
static demo when the tools share an origin. It is not a server-side case
record or a replacement for an approved evidence-management system.

## Flexible note format

No rigid template — a line can start with an ISO date (`2026-08-28T18:41`), a US-style date (`8/28`, `8/28/2026`, `8/28/26`), or a month name (`Aug 28, 2026`), with an optional 12- or 24-hour time, separated from the note by a dash, colon, comma, or nothing at all. Lines with no year default to a "case year" you set; lines with no time are still placed but marked as time-not-specified.

## Web demo

Loads prefilled with the `simulated-account` fixture's history and renders it visually — numbered/icon markers, one entry per row, gap warnings inline (stated in whole days, e.g. "Gap of 2 days"). A **Timeline range** filter defaults to the suspected fraud dates, so the view starts focused; widen it to bring earlier context in.

- **Adding an event:** if it clearly matches a known event (e.g. "added beneficiary"), the date/time fills in automatically. If it doesn't match anything, you're prompted to set the date/time yourself. Choose an event type and optional source/context so free-form notes remain useful during review. The range auto-widens to include new events.
- **Select event:** click "Select event" to enter edit mode, then click any entry to edit its text, type, source, or date/time (it re-sorts), or delete it (behind a confirm step).
- **Export JSON:** downloads the full chronological timeline with source and time-known fields.

## Python CLI

Accepts a JSON file of structured events, or a plain `.txt` file of free-text note lines using the same flexible parsing as the web demo. Outputs a chronological timeline in Markdown.

```
python case_timeline_builder.py notes.json --gap-hours 72 -o timeline.md
python case_timeline_builder.py notes.txt --case-year 2026 -o timeline.md
```

## Privacy Mode

The 🔒 Privacy Mode toggle (top right, shared across the suite via
`localStorage`) is here for consistency with the other tools. Timeline entries
are investigator-authored, so they are not automatically classified as PII;
avoid placing unnecessary sensitive data in free-form notes.

## Other tools in this series

- [Case Calculator](https://biancabcarlson.github.io/Case-Calculator/)
- [Report Builder](https://biancabcarlson.github.io/Report-Builder/)
- [OSINT Assistant](https://biancabcarlson.github.io/OSINT-Assistant/)
- [Documents Folder](https://biancabcarlson.github.io/Documents-Folder/)
- [Entity Match](https://biancabcarlson.github.io/Entity-Match/)
- [Timeline Builder](https://biancabcarlson.github.io/Timeline-Builder/) *(this repo)*
