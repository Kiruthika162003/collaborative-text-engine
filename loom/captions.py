"""Captions: figures and tables numbered by kind and order, never by hand.

A figure caption carries a number, and hand-numbered figures
suffer the ordered list's exact disease: insert Figure 2 and
every later figure is misnumbered until someone renumbers
them all. So this computes the numbers from reading order
instead, walking the visible cloth and handing each caption
the next number for its kind, figures counted apart from
tables apart from listings, so Figure 1 and Table 1 coexist
and neither disturbs the other's count. A caption is a line
that opens with a known kind and a colon, Figure: the river
at dawn, and its number is never stored, so a figure dropped
in above the others renumbers the rest for free the next
time the captions are read, which is the whole point of
computing rather than typing them. Each caption pins to its
line's first strand, so a reference to Figure 3 by pin still
finds the right figure after figures move, the anchor
discipline every list in this codebase keeps. The list of
figures and the list of tables are rendered from the same
walk, in reading order, which is where a reader expects to
find them, and a document with no captions of a kind reports
that plainly rather than printing an empty heading over
nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave

KINDS = ("Figure", "Table", "Listing", "Equation")
CAPTION = re.compile(
    r"^(" + "|".join(KINDS) + r"):\s*(.+)$"
)


@dataclass(frozen=True)
class Caption:
    kind: str
    number: int
    text: str
    pin: OpId

    def label(self) -> str:
        return f"{self.kind} {self.number}"


def _visible_lines(weave: Weave) -> list[tuple[OpId | None, str]]:
    lines: list[tuple[OpId | None, str]] = []
    glyphs: list[str] = []
    first: OpId | None = None
    for strand in weave.strands:
        if strand.sheared:
            continue
        if strand.glyph == "\n":
            lines.append((first, "".join(glyphs)))
            glyphs = []
            first = None
            continue
        if first is None:
            first = strand.id
        glyphs.append(strand.glyph)
    lines.append((first, "".join(glyphs)))
    return lines


def captions(weave: Weave) -> list[Caption]:
    counters: dict[str, int] = {}
    result: list[Caption] = []
    for pin, text in _visible_lines(weave):
        match = CAPTION.match(text.strip())
        if match is None or pin is None:
            continue
        kind = match.group(1)
        counters[kind] = counters.get(kind, 0) + 1
        result.append(
            Caption(
                kind=kind,
                number=counters[kind],
                text=match.group(2).strip(),
                pin=pin,
            )
        )
    return result


def of_kind(weave: Weave, kind: str) -> list[Caption]:
    return [
        caption for caption in captions(weave) if caption.kind == kind
    ]


def list_of(weave: Weave, kind: str) -> str:
    found = of_kind(weave, kind)
    if not found:
        return f"no {kind.lower()}s in this document"
    return "\n".join(
        f"{caption.label()}: {caption.text}" for caption in found
    )


def report(weave: Weave) -> str:
    found = captions(weave)
    if not found:
        return "no captions; the document has no figures or tables"
    counts: dict[str, int] = {}
    for caption in found:
        counts[caption.kind] = counts.get(caption.kind, 0) + 1
    parts = ", ".join(
        f"{count} {kind.lower()}(s)"
        for kind, count in sorted(counts.items())
    )
    return f"{len(found)} caption(s): {parts}"
