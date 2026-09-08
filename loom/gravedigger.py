"""The gravedigger: tombstones collected only when the whole room is quiet.

Tombstones are the rent convergence pays, and the
gravedigger is how the rent comes back, under one rule
stated without apology: collection happens at quiescence,
every vector in the circle identical, and the whole circle
collects together. The rule is strict because the unsafe
cases are quiet ones. An in-flight insert may anchor on a
dead strand its author had not yet seen die; a circle
where one site collects early and another late can seat a
future sibling differently, positions having shifted under
one walk and not the other. Quiescence dissolves both:
nothing is in flight, and identical fabrics collected by
an identical rule produce identical fabrics again. The
collection itself splices origins, a surviving strand
anchored on the dead re-anchored through the grave chain
to its nearest living ancestor, so future integrations
never ask the index for a strand that is gone. The horizon
vector, the pointwise minimum of everyone's clocks, is
computed and reported because it is the number operators
ask for, how far behind is the slowest of us, even though
this gravedigger's law is stricter than the horizon.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.circle import Circle
from loom.clock import VersionVector
from loom.errors import Invalid
from loom.snapshot import fabric_digest
from loom.weave import HEAD, Weave


def horizon(
    vectors: list[VersionVector],
) -> VersionVector:
    if not vectors:
        raise Invalid(
            "a horizon of no clocks is midnight "
            "everywhere"
        )
    sites = set()
    for vector in vectors:
        sites |= set(vector.seen)
    floor = VersionVector()
    for site in sites:
        lowest = min(
            vector.top(site) for vector in vectors
        )
        if lowest > 0:
            floor.seen[site] = lowest
    return floor


def quiescent(circle: Circle) -> bool:
    wires = {
        author.clock.wire()
        for author in circle.authors.values()
    }
    return len(wires) == 1


def collect(weave: Weave) -> tuple[int, str]:
    doomed = {
        strand.id
        for strand in weave.strands
        if strand.sheared
    }
    origin_of = {
        strand.id: strand.origin
        for strand in weave.strands
    }

    def living_ancestor(op_id):
        cursor = op_id
        while cursor is not HEAD and cursor in doomed:
            cursor = origin_of[cursor]
        return cursor

    survivors = []
    spliced = 0
    for strand in weave.strands:
        if strand.sheared:
            continue
        if (
            strand.origin is not HEAD
            and strand.origin in doomed
        ):
            strand.origin = living_ancestor(
                strand.origin
            )
            spliced += 1
        survivors.append(strand)
    weave.strands = survivors
    weave.by_id = {
        strand.id: index
        for index, strand in enumerate(survivors)
    }
    return len(doomed), (
        f"{len(doomed)} grave(s) cleared, "
        f"{spliced} origin(s) spliced to living "
        f"ancestors, {len(survivors)} strand(s) remain"
    )


@dataclass
class Gravedigger:
    swept: int = 0

    def sweep(self, circle: Circle) -> str:
        if not quiescent(circle):
            wires = sorted(
                {
                    author.clock.wire()
                    for author in (
                        circle.authors.values()
                    )
                }
            )
            raise Invalid(
                "the gravedigger works only in a "
                "quiet room and someone is still "
                f"speaking; {len(wires)} different "
                "clocks in the circle"
            )
        cleared = 0
        receipts = []
        for site in sorted(circle.authors):
            weave = circle.authors[site].weave
            count, receipt = collect(weave)
            cleared += count
            receipts.append(f"{site}: {receipt}")
        digests = {
            fabric_digest(author.weave)
            for author in circle.authors.values()
        }
        if len(digests) != 1:
            raise Invalid(
                "identical fabrics collected by an "
                "identical rule produced different "
                "fabrics; the rule is broken, stop "
                "everything"
            )
        self.swept += 1
        return "\n".join(
            [
                f"sweep #{self.swept}: {cleared} "
                "grave(s) cleared across "
                f"{len(circle.authors)} site(s), one "
                "fabric digest afterward",
                *[f"  {line}" for line in receipts],
            ]
        )
