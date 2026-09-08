"""Marks: formatting pinned to strands, because positions are weather.

A bold range remembered as offsets four through nine is
wrong by breakfast in a shared document; the wardrobe pins
every mark to strand ids, the start and the end of the
dressed stretch, and lets the fabric's own order say what
lies between. The order of two existing strands never
changes under integration, arrivals only land between, so
a mark valid where it was minted is valid everywhere
forever, and a glyph typed inside a dressed stretch wears
the dress automatically, being between the pins. Marks
remove by instance, not by name: stripping unpins the one
mark you observed, and a concurrent bolding by someone
else survives, add-wins the way shared intentions should
win. Endpoints may die and keep serving, a tombstoned pin
holding its place in the order exactly as tombstones hold
everything else here, and a mark minted backwards, end
before start in the fabric, is refused at the door,
because no ordering of arrivals will ever turn it around.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from loom.errors import Invalid, Missing
from loom.ids import OpId
from loom.weave import Weave

STYLE_PATTERN = re.compile(r"^[a-z][a-z-]*$")


@dataclass(frozen=True)
class Mark:
    id: OpId
    style: str
    start: OpId
    end: OpId

    def __post_init__(self) -> None:
        if not STYLE_PATTERN.match(self.style):
            raise Invalid(
                f"{self.style!r} is not a style name; "
                "lowercase words, because styles are "
                "vocabulary and vocabulary is shared"
            )


@dataclass(frozen=True)
class Unmark:
    id: OpId
    mark_id: OpId


@dataclass
class Wardrobe:
    weave: Weave
    marks: dict[OpId, Mark] = field(default_factory=dict)
    stripped: set[OpId] = field(default_factory=set)

    def _position(self, op_id: OpId) -> int:
        held = self.weave.by_id.get(op_id)
        if held is None:
            raise Missing(
                f"{op_id.wire()} is not in the "
                "fabric; a pin needs a strand. "
                "Buffer it"
            )
        return held

    def dress(self, mark: Mark) -> str:
        if mark.id in self.marks:
            return (
                f"{mark.id.wire()} already dressed; "
                "one mark, one instance"
            )
        start_pos = self._position(mark.start)
        end_pos = self._position(mark.end)
        if start_pos > end_pos:
            raise Invalid(
                f"{mark.style} pinned backwards, end "
                "before start in the fabric; no "
                "ordering of arrivals will turn it "
                "around"
            )
        self.marks[mark.id] = mark
        return (
            f"{mark.style} dressed from "
            f"{mark.start.wire()} to {mark.end.wire()}"
        )

    def strip(self, unmark: Unmark) -> str:
        if unmark.mark_id in self.stripped:
            return (
                f"{unmark.mark_id.wire()} already "
                "stripped; one strip suffices"
            )
        if unmark.mark_id not in self.marks:
            raise Missing(
                f"{unmark.mark_id.wire()} is not a "
                "mark this wardrobe has seen; "
                "stripping removes what was observed. "
                "Buffer it"
            )
        self.stripped.add(unmark.mark_id)
        style = self.marks[unmark.mark_id].style
        return (
            f"{style} stripped by instance; a "
            "concurrent dressing survives, add-wins "
            "the way shared intentions should"
        )

    def _standing(self) -> list[Mark]:
        return [
            mark
            for mark_id, mark in self.marks.items()
            if mark_id not in self.stripped
        ]

    def styles_at(self, strand_id: OpId) -> frozenset:
        position = self._position(strand_id)
        found = set()
        for mark in self._standing():
            if (
                self._position(mark.start)
                <= position
                <= self._position(mark.end)
            ):
                found.add(mark.style)
        return frozenset(found)

    def spans(self) -> list[tuple[str, frozenset]]:
        runs: list[tuple[str, frozenset]] = []
        for strand in self.weave.strands:
            if strand.sheared:
                continue
            dressed = self.styles_at(strand.id)
            if runs and runs[-1][1] == dressed:
                runs[-1] = (
                    runs[-1][0] + strand.glyph,
                    dressed,
                )
            else:
                runs.append((strand.glyph, dressed))
        return runs

    def census(self) -> str:
        standing = self._standing()
        return (
            f"{len(standing)} mark(s) standing, "
            f"{len(self.stripped)} stripped; "
            "positions are weather, pins are law"
        )
