"""Checkpoints: moments shelved by name, and the road between them measured.

A checkpoint is a snapshot with a name and a promise: the
name never moves. Keeping the same name twice is refused
outright, because a checkpoint that can be quietly
re-kept is a bookmark that slides while you sleep, and
every recall thaws the full fabric, tombstones and all,
so a recalled moment can rejoin the living conversation
rather than just being looked at. The road between two
checkpoints is measured on the visible cloth with the
matcher counting three honest quantities, glyphs kept,
glyphs added, glyphs dropped, and the direction is stated
in the report because a diff without a direction is a
riddle: the road reads from the older name to the newer
as given, and reversing the names reverses the verbs.
The shelf lists its moments in keeping order, the order
a writer's day actually happened.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher

from loom.errors import Invalid, Missing
from loom.snapshot import fabric_digest, freeze, thaw
from loom.weave import Weave


@dataclass
class Shelf:
    kept: dict[str, str] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)

    def keep(self, name: str, weave: Weave) -> str:
        if not name.strip():
            raise Invalid(
                "a checkpoint needs a name; moments "
                "without names are just the past"
            )
        if name in self.kept:
            raise Invalid(
                f"{name!r} is already kept; a "
                "checkpoint that can be re-kept is a "
                "bookmark that slides while you sleep"
            )
        self.kept[name] = freeze(weave)
        self.order.append(name)
        return (
            f"{name!r} shelved at "
            f"{fabric_digest(weave)}"
        )

    def recall(self, name: str) -> Weave:
        page = self.kept.get(name)
        if page is None:
            raise Missing(
                f"{name!r} was never shelved; the "
                "shelf holds "
                + (
                    ", ".join(
                        repr(held)
                        for held in self.order
                    )
                    or "nothing"
                )
            )
        return thaw(page)

    def road(self, older: str, newer: str) -> str:
        before = self.recall(older).text()
        after = self.recall(newer).text()
        matcher = SequenceMatcher(
            a=before, b=after, autojunk=False
        )
        kept = added = dropped = 0
        for verb, a0, a1, b0, b1 in (
            matcher.get_opcodes()
        ):
            if verb == "equal":
                kept += a1 - a0
            elif verb == "insert":
                added += b1 - b0
            elif verb == "delete":
                dropped += a1 - a0
            else:
                dropped += a1 - a0
                added += b1 - b0
        return (
            f"from {older!r} to {newer!r}: "
            f"{kept} glyph(s) kept, {added} added, "
            f"{dropped} dropped; reversing the names "
            "reverses the verbs"
        )

    def listing(self) -> str:
        if not self.order:
            return (
                "an empty shelf; no moment has been "
                "worth a name yet"
            )
        lines = [
            f"{len(self.order)} moment(s), in the "
            "order the day happened:"
        ]
        lines.extend(
            f"  {name}" for name in self.order
        )
        return "\n".join(lines)
