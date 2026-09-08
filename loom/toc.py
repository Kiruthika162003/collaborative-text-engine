"""Table of contents: an outline rendered with numbers and anchors that hold.

A table of contents is the heading tree turned into
navigation, and this renders it two ways a reader needs:
an indented list for the eye and a numbered outline, one,
one point one, one point two, two, for the citation. The
numbers are computed from the tree, restarting a level's
count under each new parent and never continuing across a
gap, because a contents whose numbers do not match the
nesting is a map disagreeing with its own legend. Each
entry carries the strand id of its heading so a contents
link jumps to the right section even after sections move,
the same pin every anchor in the loom trusts, and a
contents built before an edit still points correctly after
it. A heading that skipped a level, a one followed by a
three, is numbered as what it is rather than promoted to
fill the gap, and the anomaly is left visible in the
numbering because a contents that quietly renumbers a
broken hierarchy hides the very thing the writer needs to
fix. An empty document has no contents, reported plainly
rather than as a heading called nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.headings import headings
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Entry:
    number: str
    title: str
    level: int
    pin: OpId


def entries(weave: Weave) -> list[Entry]:
    found = headings(weave)
    counters: list[int] = []
    result: list[Entry] = []
    for heading in found:
        while len(counters) < heading.level:
            counters.append(0)
        while len(counters) > heading.level:
            counters.pop()
        counters[heading.level - 1] += 1
        for deeper in range(
            heading.level, len(counters)
        ):
            counters[deeper] = 0
        number = ".".join(
            str(c)
            for c in counters[: heading.level]
        )
        result.append(
            Entry(
                number=number,
                title=heading.title,
                level=heading.level,
                pin=heading.pin,
            )
        )
    return result


def numbered(weave: Weave) -> str:
    found = entries(weave)
    if not found:
        return "no contents; the document has no headings"
    return "\n".join(
        f"{entry.number} {entry.title}"
        for entry in found
    )


def indented(weave: Weave) -> str:
    found = entries(weave)
    if not found:
        return "no contents; the document has no headings"
    return "\n".join(
        "  " * (entry.level - 1) + entry.title
        for entry in found
    )
