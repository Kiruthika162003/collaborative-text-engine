"""Cadence: the rhythm of a session read from the tape's own order.

Without wall-clock timestamps the loom still knows a
session's rhythm, because a tape records operations in the
order they were woven, and that order carries the shape of
the collaboration: a burst is a maximal run of operations
from one hand before another takes a turn, and the run of
bursts is the call and response of people writing together.
This measures the bursts, their count, the longest, the
average length, and the number of times the pen changed
hands, which is the number that distinguishes a document
one person wrote while others watched from one genuinely
passed back and forth. Shears count as gestures because
deleting is participating, and a solo tape reports one
burst and zero handoffs, the honest signature of a
monologue. The busiest hand is named by total gestures,
not by bursts, because someone who typed steadily in a
few long turns contributed more than someone who
interjected constantly, and cadence measures work, not
noise.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.transcript import Tape


@dataclass(frozen=True)
class Burst:
    site: str
    length: int


def bursts(tape: Tape) -> list[Burst]:
    found: list[Burst] = []
    for op in tape.reel:
        site = op.id.site
        if found and found[-1].site == site:
            last = found[-1]
            found[-1] = Burst(
                site=site, length=last.length + 1
            )
        else:
            found.append(Burst(site=site, length=1))
    return found


def handoffs(tape: Tape) -> int:
    runs = bursts(tape)
    return max(0, len(runs) - 1)


def busiest_hand(tape: Tape) -> str | None:
    totals: dict[str, int] = {}
    for op in tape.reel:
        totals[op.id.site] = (
            totals.get(op.id.site, 0) + 1
        )
    if not totals:
        return None
    return max(
        totals,
        key=lambda site: (totals[site], site),
    )


def report(tape: Tape) -> str:
    runs = bursts(tape)
    if not runs:
        return "an empty tape has no rhythm"
    longest = max(run.length for run in runs)
    average = sum(run.length for run in runs) / len(
        runs
    )
    return (
        f"{len(runs)} burst(s), {handoffs(tape)} "
        f"handoff(s), longest {longest}, average "
        f"{average:.1f}, busiest {busiest_hand(tape)}; "
        "cadence measures work, not noise"
    )
