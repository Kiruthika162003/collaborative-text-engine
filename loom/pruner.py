"""The pruner: the journal trimmed to a safe horizon, never past it.

Journals grow without bound, and the pruner is how they
stop, under a rule as strict as the gravedigger's and for
the same reason: an operation may be forgotten only once
every replica in a known set has been observed to hold it,
the horizon being the pointwise minimum of everyone's
clocks. Below the horizon, an operation can never be asked
for again, because everyone already has it; above it, some
peer may still request it, and forgetting there is how a
lagging replica gets stranded asking for history nobody
kept. The pruner takes the horizon as a promise the caller
must earn, not a number it invents, and reports what it
dropped and what it kept, because a retention policy whose
effects are invisible is indistinguishable from a leak.
Pruning never touches the weave, only the journal's memory
for sync, so a pruned station still renders every glyph it
ever wove; it has simply forgotten how to teach the past to
someone who was not there.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.clock import VersionVector
from loom.errors import Invalid
from loom.journal import Journal


@dataclass
class Pruner:
    dropped_total: int = 0

    def prune(
        self,
        journal: Journal,
        horizon: VersionVector,
    ) -> str:
        before = journal.size()
        kept: dict = {}
        dropped = 0
        for op_id, op in journal.entries.items():
            if horizon.has(op_id):
                dropped += 1
            else:
                kept[op_id] = op
        journal.entries = kept
        self.dropped_total += dropped
        return (
            f"pruned {dropped} of {before} "
            f"operation(s) below the horizon, "
            f"{len(kept)} kept; a lagging replica can "
            "still be taught everything above it"
        )

    def safe_horizon(
        self, clocks: list[VersionVector]
    ) -> VersionVector:
        if not clocks:
            raise Invalid(
                "a horizon over no replicas is a "
                "promise to nobody; name the set"
            )
        sites: set[str] = set()
        for clock in clocks:
            sites |= set(clock.seen)
        floor = VersionVector()
        for site in sites:
            lowest = min(
                clock.top(site) for clock in clocks
            )
            if lowest > 0:
                floor.seen[site] = lowest
        return floor
