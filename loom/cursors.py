"""Cursors: everyone's place held by a strand, not by a number.

A cursor stored as offset twelve is pointing at a
different word every time anyone types, which is why
shared editors twitch; here a caret anchors to the strand
left of it, or to the head, and its visible position is
recomputed from the fabric whenever asked, the count of
living glyphs at or before the anchor. Anchoring buys the
two behaviors humans expect without code asking for them:
text inserted upstream shifts the caret right because the
count grows, and the caret whose anchor is sheared stays
exactly where the tombstone stands, holding its place at
a funeral the way a bookmark holds a torn-out page. The
parlor tracks one caret per hand, placing is idempotent
in effect since a hand has one place, and the roster
reads every caret with the glyph it touches, because
presence is a social feature and social features are
read aloud.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Missing
from loom.ids import OpId, check_site
from loom.weave import HEAD, Weave


@dataclass(frozen=True)
class Caret:
    site: str
    anchor: OpId | None


@dataclass
class Parlor:
    weave: Weave
    carets: dict[str, Caret] = field(
        default_factory=dict
    )

    def place(self, site: str, index: int) -> Caret:
        check_site(site)
        anchor = self.weave.origin_for_insert_at(index)
        caret = Caret(site=site, anchor=anchor)
        self.carets[site] = caret
        return caret

    def park(self, site: str) -> str:
        if site not in self.carets:
            raise Missing(
                f"{site} holds no place here"
            )
        del self.carets[site]
        return f"{site} parked; the place is released"

    def visible_position(self, site: str) -> int:
        caret = self.carets.get(site)
        if caret is None:
            raise Missing(
                f"{site} holds no place here"
            )
        if caret.anchor is HEAD:
            return 0
        anchor_index = self.weave.by_id.get(
            caret.anchor
        )
        if anchor_index is None:
            raise Missing(
                f"{site} anchors on "
                f"{caret.anchor.wire()}, which this "
                "fabric has never seen"
            )
        position = 0
        for strand in self.weave.strands[
            : anchor_index + 1
        ]:
            if not strand.sheared:
                position += 1
        return position

    def glyph_touched(self, site: str) -> str:
        position = self.visible_position(site)
        if position == 0:
            return "(the head)"
        return repr(
            self.weave.strand_at_visible(
                position - 1
            ).glyph
        )

    def roster(self) -> str:
        if not self.carets:
            return (
                "an empty parlor; nobody is holding "
                "a place"
            )
        lines = [
            f"{len(self.carets)} caret(s) in the "
            "parlor:"
        ]
        for site in sorted(self.carets):
            lines.append(
                f"  {site} at "
                f"{self.visible_position(site)}, "
                f"touching {self.glyph_touched(site)}"
            )
        return "\n".join(lines)
