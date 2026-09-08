"""The reading room: search that hands back pins, not page numbers.

A search result reported as offset forty is stale the
moment anyone types upstream, so the reading room answers
with bookmarks, the ids of the first and last strand of
each occurrence, and a bookmark is a claim that can be
re-checked forever: still_says walks the living glyphs
between its two pins and reports whether the cloth still
reads the needle there, staying honest when an edit lands
inside the stretch and turns yesterday's match into
today's near-miss. Finding runs on the visible cloth only,
the dead being unsearchable on purpose since nobody means
to find what was deleted, and the empty needle is refused
at the door because it matches everywhere, and a result
set of everywhere is a result set of nothing usable. The
census counts occurrences the way readers do, overlapping
matches included, and says so, since aaa contains aa
twice to anyone who actually looks.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Invalid
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Bookmark:
    first: OpId
    last: OpId
    found_at: int


def _visible_strands(weave: Weave):
    return [
        strand
        for strand in weave.strands
        if not strand.sheared
    ]


def find(weave: Weave, needle: str) -> list[Bookmark]:
    if not needle:
        raise Invalid(
            "the empty needle matches everywhere, "
            "and everywhere is nothing usable"
        )
    visible = _visible_strands(weave)
    cloth = "".join(
        strand.glyph for strand in visible
    )
    marks: list[Bookmark] = []
    start = 0
    while True:
        found = cloth.find(needle, start)
        if found < 0:
            return marks
        marks.append(
            Bookmark(
                first=visible[found].id,
                last=visible[
                    found + len(needle) - 1
                ].id,
                found_at=found,
            )
        )
        start = found + 1


def count(weave: Weave, needle: str) -> int:
    return len(find(weave, needle))


def still_says(
    weave: Weave, bookmark: Bookmark, needle: str
) -> bool:
    first_pos = weave.by_id.get(bookmark.first)
    last_pos = weave.by_id.get(bookmark.last)
    if first_pos is None or last_pos is None:
        return False
    stretch = "".join(
        strand.glyph
        for strand in weave.strands[
            first_pos : last_pos + 1
        ]
        if not strand.sheared
    )
    return stretch == needle


def current_position(
    weave: Weave, bookmark: Bookmark
) -> int:
    first_pos = weave.by_id.get(bookmark.first)
    if first_pos is None:
        raise Invalid(
            "the bookmark's first pin left the "
            "fabric; there is no current position "
            "for a place that is gone"
        )
    return sum(
        1
        for strand in weave.strands[:first_pos]
        if not strand.sheared
    )


def census(weave: Weave, needle: str) -> str:
    total = count(weave, needle)
    return (
        f"{needle!r} occurs {total} time(s), "
        "overlaps included; aaa contains aa twice "
        "to anyone who actually looks"
    )
