"""Selections: each hand's highlighted range, presence that is not content.

A selection is what a collaborator has highlighted right
now, and it is emphatically not part of the document: it
belongs to the person, it changes constantly, and it
vanishes when they look away, so storing it in the fabric
would be storing a mouse position in a novel. The gallery
keeps one selection per hand, pinned to the first and last
strand of the range like everything else that must survive
edits, and answers the questions a presence sidebar asks:
who is selecting, what text each has, and whether two
people's selections overlap, which is the signal that a
conflict is about to be typed and the moment to nudge them
into conversation. A collapsed selection, first and last
the same strand, is a bare cursor and reads as such rather
than as a zero-width highlight, because the distinction
between pointing and selecting is one every editor user
feels even when they cannot name it. Selections on sheared
strands are dropped rather than shown against tombstones,
because unlike a comment, a highlight of deleted text is
not a remark that outlives its subject, it is a stale
pointer, and the honest thing is to let it go.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.ids import OpId, check_site
from loom.weave import Weave


@dataclass(frozen=True)
class Selection:
    site: str
    first: OpId
    last: OpId


@dataclass
class Gallery:
    weave: Weave
    selections: dict[str, Selection] = field(
        default_factory=dict
    )

    def select(
        self, site: str, first: OpId, last: OpId
    ) -> str:
        check_site(site)
        self.selections[site] = Selection(
            site=site, first=first, last=last
        )
        return f"{site} selecting {self.text_of(site)!r}"

    def clear(self, site: str) -> str:
        if site in self.selections:
            del self.selections[site]
            return f"{site} looked away"
        return f"{site} had nothing selected"

    def _range(self, selection: Selection):
        first = self.weave.by_id.get(selection.first)
        last = self.weave.by_id.get(selection.last)
        if first is None or last is None:
            return None
        first_strand = self.weave.strands[first]
        last_strand = self.weave.strands[last]
        if (
            first_strand.sheared
            or last_strand.sheared
        ):
            return None
        return first, last

    def text_of(self, site: str) -> str:
        selection = self.selections.get(site)
        if selection is None:
            return ""
        span = self._range(selection)
        if span is None:
            return ""
        first, last = span
        return "".join(
            strand.glyph
            for strand in self.weave.strands[
                first : last + 1
            ]
            if not strand.sheared
        )

    def is_cursor(self, site: str) -> bool:
        selection = self.selections.get(site)
        return (
            selection is not None
            and selection.first == selection.last
        )

    def overlaps(self, one: str, two: str) -> bool:
        first = self.selections.get(one)
        second = self.selections.get(two)
        if first is None or second is None:
            return False
        a = self._range(first)
        b = self._range(second)
        if a is None or b is None:
            return False
        return a[0] <= b[1] and b[0] <= a[1]

    def collisions(self) -> list[tuple[str, str]]:
        sites = sorted(self.selections)
        found = []
        for i, one in enumerate(sites):
            for two in sites[i + 1 :]:
                if self.overlaps(one, two):
                    found.append((one, two))
        return found

    def sidebar(self) -> str:
        living = [
            site
            for site in sorted(self.selections)
            if self._range(self.selections[site])
            is not None
        ]
        if not living:
            return "nobody is selecting anything"
        lines = [f"{len(living)} hand(s) present:"]
        for site in living:
            if self.is_cursor(site):
                lines.append(
                    f"  {site}: cursor, not selecting"
                )
            else:
                lines.append(
                    f"  {site}: {self.text_of(site)!r}"
                )
        for one, two in self.collisions():
            lines.append(
                f"  {one} and {two} overlap; a "
                "conflict is about to be typed"
            )
        return "\n".join(lines)
