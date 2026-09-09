"""Growth: the document's size over a session, read from the tape's own order.

The cadence module reads a session's rhythm from the tape;
this reads its size. Walking the tape in the order operations
were woven, each insert adds a glyph and each shear takes one
away, so the running total is the document's size after every
gesture, a curve that tells the shape of the work: steady
growth, a long plateau, a late cut that shrank a draft. From
that curve fall the numbers a facilitator asks. The net growth
is where the curve ends, inserts minus shears, the glyphs that
survived the session. The peak is the curve's highest point
and where it fell, which distinguishes a document that grew to
its final size from one that ballooned and was cut back, two
very different sessions with the same ending. And the churn is
the count of shears, the deletions, a measure of rework that a
net growth alone hides, since a document that ended at a
hundred glyphs after typing a hundred is a different session
from one that ended at a hundred after typing three hundred
and cutting two. The curve is size over operation order, not
over wall-clock, because the tape records order and not time,
and this says so rather than implying a clock it does not
have; order is the honest axis, and for reading the shape of
collaboration it is the one that matters.
"""

from __future__ import annotations

from loom.transcript import Tape
from loom.weave import Insert


def growth_curve(tape: Tape) -> list[int]:
    curve = []
    size = 0
    for op in tape.reel:
        size += 1 if isinstance(op, Insert) else -1
        curve.append(size)
    return curve


def net_growth(tape: Tape) -> int:
    curve = growth_curve(tape)
    return curve[-1] if curve else 0


def churn(tape: Tape) -> int:
    return sum(1 for op in tape.reel if not isinstance(op, Insert))


def peak(tape: Tape) -> tuple[int, int]:
    curve = growth_curve(tape)
    if not curve:
        return (0, -1)
    high = max(curve)
    return (high, curve.index(high))


def report(tape: Tape) -> str:
    if not tape.reel:
        return "an empty tape has no growth"
    high, when = peak(tape)
    return (
        f"net growth {net_growth(tape)} glyph(s), peak {high} "
        f"at operation {when}, churn {churn(tape)} deletion(s); "
        "size over operation order, not wall-clock"
    )
