"""Dates: the dates in the prose found and normalized, with the ambiguous ones left so.

Dates arrive in a document in every format a writer knows,
and this finds the common ones, the ISO year-month-day, the
twelfth of March, March the twelfth, and the slash form, and
normalizes each to one canonical spelling so a reader or a
sorter can compare them. The written forms normalize cleanly
because their parts are labelled: a month spelled out cannot
be mistaken for a day. The slash form is where honesty
earns its keep, because 05/06/2024 is the fifth of June to
half the world and the sixth of May to the other half, and a
date parser that picked one convention would silently
misread every date from the other. So a slash date is
normalized only when one number settles it, a value above
twelve that can only be a day, and left flagged as ambiguous
when both numbers could be either, because a wrong date
presented as certain is worse than a date the reader is told
to check. Each date pins to the strand where it starts so a
list of a document's dates survives edits above them, and the
ranges are not double counted when two patterns could claim
the same span, the first match holding it. Two-digit years
and time-of-day are out of scope and named as such, since the
formats here are the ones a writing room actually types and a
fuller parser would be a calendar library the feature does
not need.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave

MONTHS = {}
for _index, _name in enumerate(
    [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
    ],
    start=1,
):
    MONTHS[_name] = _index
    MONTHS[_name[:3]] = _index

_NAMES = "|".join(sorted(MONTHS, key=len, reverse=True))
ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DMY = re.compile(rf"\b(\d{{1,2}})\s+({_NAMES})\s+(\d{{4}})\b", re.IGNORECASE)
MDY = re.compile(rf"\b({_NAMES})\s+(\d{{1,2}}),?\s+(\d{{4}})\b", re.IGNORECASE)
SLASH = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")


@dataclass(frozen=True)
class Found:
    text: str
    iso: str | None
    pin: OpId
    position: int
    ambiguous: bool


def _visible_ids(weave: Weave) -> list[OpId]:
    return [
        strand.id for strand in weave.strands if not strand.sheared
    ]


def _slash_iso(first: int, second: int, year: int) -> tuple[str | None, bool]:
    if first > 12 and second <= 12:
        return f"{year:04d}-{second:02d}-{first:02d}", False
    if second > 12 and first <= 12:
        return f"{year:04d}-{first:02d}-{second:02d}", False
    if first > 12 and second > 12:
        return None, False
    return None, True


def dates(weave: Weave) -> list[Found]:
    text = weave.text()
    ids = _visible_ids(weave)
    claimed: list[tuple[int, int]] = []
    found: list[Found] = []

    def free(start: int, end: int) -> bool:
        return not any(
            start < other_end and other_start < end
            for other_start, other_end in claimed
        )

    def add(match: re.Match, iso: str | None, ambiguous: bool) -> None:
        if not free(match.start(), match.end()):
            return
        claimed.append((match.start(), match.end()))
        found.append(
            Found(
                text=match.group(0),
                iso=iso,
                pin=ids[match.start()],
                position=match.start(),
                ambiguous=ambiguous,
            )
        )

    for match in ISO.finditer(text):
        add(match, match.group(0), False)
    for match in DMY.finditer(text):
        day, month, year = (
            int(match.group(1)),
            MONTHS[match.group(2).lower()],
            int(match.group(3)),
        )
        add(match, f"{year:04d}-{month:02d}-{day:02d}", False)
    for match in MDY.finditer(text):
        month, day, year = (
            MONTHS[match.group(1).lower()],
            int(match.group(2)),
            int(match.group(3)),
        )
        add(match, f"{year:04d}-{month:02d}-{day:02d}", False)
    for match in SLASH.finditer(text):
        iso, ambiguous = _slash_iso(
            int(match.group(1)), int(match.group(2)), int(match.group(3))
        )
        add(match, iso, ambiguous)

    return sorted(found, key=lambda item: item.position)


def normalized(weave: Weave) -> list[str]:
    return [item.iso for item in dates(weave) if item.iso is not None]


def ambiguous(weave: Weave) -> list[Found]:
    return [item for item in dates(weave) if item.ambiguous]


def report(weave: Weave) -> str:
    found = dates(weave)
    if not found:
        return "no dates found in the prose"
    unclear = len(ambiguous(weave))
    return (
        f"{len(found)} date(s), {unclear} ambiguous; "
        f"normalized: {', '.join(normalized(weave)) or 'none'}"
    )
