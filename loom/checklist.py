"""Checklist: list items whose done-state converges, checked by many hands.

A shared checklist is a list where every item also carries
a done-state that anyone may toggle, and the toggling is
where naive implementations lose ticks: two people checking
and unchecking the same item at once must converge, so the
done-state is a small last-writer-wins flag keyed by the
item's anchor strand and decided by witness rank with site
breaking ties, the weave's own order. Checking an item that
does not exist is refused rather than silently created,
because a checkmark floating free of any item is a state
nobody can see or clear. The progress is live and honest:
done over total, computed from the current items so an item
deleted from the list stops counting toward either number,
which is what a reader expects when they remove a task
rather than completing it. A concurrent check and uncheck
resolve to whichever hand had witnessed more, and the tie,
equal rank, goes to the higher site name, arbitrary and
identical everywhere, because a checklist that shows
different progress to two people is worse than no
checklist.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Missing
from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Toggle:
    anchor: OpId
    done: bool
    rank: int
    site: str

    def seat_key(self) -> tuple[int, str]:
        return (self.rank, self.site)


@dataclass
class Checklist:
    weave: Weave
    flags: dict = field(default_factory=dict)

    def toggle(self, toggle: Toggle) -> str:
        if toggle.anchor not in self.weave.by_id:
            raise Missing(
                f"{toggle.anchor.wire()} is not an "
                "item anchor; a checkmark floating "
                "free is a state nobody can clear"
            )
        held = self.flags.get(toggle.anchor)
        if (
            held is None
            or toggle.seat_key() > held.seat_key()
        ):
            self.flags[toggle.anchor] = toggle
            return (
                f"item {'checked' if toggle.done else 'unchecked'}"
            )
        return "toggle yielded to a later one"

    def is_done(self, anchor: OpId) -> bool:
        held = self.flags.get(anchor)
        return held is not None and held.done

    def progress(self, anchors: list[OpId]) -> str:
        living = [
            a
            for a in anchors
            if a in self.weave.by_id
            and not self.weave.strands[
                self.weave.by_id[a]
            ].sheared
        ]
        done = sum(
            1 for a in living if self.is_done(a)
        )
        total = len(living)
        if total == 0:
            return "an empty checklist; nothing to do"
        return (
            f"{done} of {total} done "
            f"({done * 100 // total}%)"
        )
