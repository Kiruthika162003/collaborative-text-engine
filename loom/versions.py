"""Versions: a timeline over checkpoints, walkable and diffable step by step.

A shelf keeps named moments; a timeline gives them an order
and a cursor, so a writer can walk backward through their
own drafts the way playback walks operations, but at the
coarser grain of saved versions rather than keystrokes. The
timeline records checkpoints in the order they were taken
and lets the cursor move to previous, next, or a named
version, clamping at the ends and saying so rather than
throwing, because a version navigator that crashes at the
first draft is a navigator nobody trusts to explore. The
step between the current version and its predecessor is a
word diff, the coarse-grained view a reviewer of revisions
actually wants, computed on demand from the two recalled
texts so the timeline stores moments and not diffs, keeping
one source of truth. A timeline of one version reports that
there is nothing to compare, the honest first-draft state,
and naming a version that was never taken is refused with
the list of the ones that were, because guessing at which
version someone meant is how a restore overwrites the wrong
draft.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.checkpoints import Shelf
from loom.errors import Invalid, Missing
from loom.worddiff import summary as word_summary


@dataclass
class Timeline:
    shelf: Shelf
    order: list = field(default_factory=list)
    cursor: int = 0

    def capture(self, name: str, weave) -> str:
        self.shelf.keep(name, weave)
        self.order.append(name)
        self.cursor = len(self.order) - 1
        return f"captured {name!r} at position {self.cursor}"

    def current(self) -> str:
        if not self.order:
            raise Invalid(
                "an empty timeline has no current "
                "version"
            )
        return self.order[self.cursor]

    def back(self) -> str:
        if self.cursor <= 0:
            return (
                "at the first draft; nothing earlier "
                "to walk to"
            )
        self.cursor -= 1
        return f"at {self.current()!r}"

    def forward(self) -> str:
        if self.cursor >= len(self.order) - 1:
            return (
                "at the latest; nothing later to walk "
                "to"
            )
        self.cursor += 1
        return f"at {self.current()!r}"

    def goto(self, name: str) -> str:
        if name not in self.order:
            raise Missing(
                f"{name!r} was never captured; the "
                "timeline holds "
                + ", ".join(
                    repr(v) for v in self.order
                )
            )
        self.cursor = self.order.index(name)
        return f"at {name!r}"

    def step_diff(self) -> str:
        if self.cursor == 0:
            return (
                "the first draft; nothing before it "
                "to compare"
            )
        older = self.order[self.cursor - 1]
        newer = self.order[self.cursor]
        counts = word_summary(
            self.shelf.recall(older).text(),
            self.shelf.recall(newer).text(),
        )
        return (
            f"from {older!r} to {newer!r}: "
            f"{counts['kept']} kept, "
            f"{counts['added']} added, "
            f"{counts['dropped']} dropped"
        )

    def timeline(self) -> str:
        if not self.order:
            return "no versions captured yet"
        lines = [f"{len(self.order)} version(s):"]
        for index, name in enumerate(self.order):
            here = (
                " <- here"
                if index == self.cursor
                else ""
            )
            lines.append(f"  {index}: {name}{here}")
        return "\n".join(lines)
