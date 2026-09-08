"""Confluence: two fabrics joined by their operations, never by their text.

The wrong way to merge two documents is to diff their text
and guess; the right way, and the only way that converges,
is to replay each side's operations into the other, because
the operations already carry the identities and origins
that make the join deterministic. Confluence takes two
tapes, the honest record of what each side wove, and builds
one fabric by applying both front to back, every operation
finding its origin present because tapes record weave order.
The result is exactly what a handshake between the two would
have produced, and the module proves it: joining two tapes
yields the same fabric digest as running both through the
mailroom in either arrival order, which is convergence
stated as an equation between two code paths that must never
disagree. Two drafts both rooted at the head join cleanly,
which is the whole point, their runs interleaving by the
same rule any concurrency uses; what is refused is the
truncated tape, an operation whose origin appears in
neither reel, because that is not a draft but a fragment,
and a fragment joined to anything produces a fabric that
is neither document and converges to nonsense.
"""

from __future__ import annotations

from loom.errors import Missing
from loom.transcript import Tape
from loom.weave import Insert, Weave


def confluence(left: Tape, right: Tape) -> Weave:
    fabric = Weave()
    seen: set = set()
    for op in list(left.reel) + list(right.reel):
        if op.id in seen:
            continue
        seen.add(op.id)
        try:
            fabric.apply(op)
        except Missing as gap:
            raise Missing(
                f"{op.id.wire()} references an "
                "origin neither tape provides; a "
                "fragment joined to anything produces "
                f"a fabric that is neither document "
                f"({gap})"
            ) from gap
    return fabric


def joined_text(left: Tape, right: Tape) -> str:
    return confluence(left, right).text()


def op_union_size(left: Tape, right: Tape) -> int:
    return len(
        {op.id for op in left.reel}
        | {op.id for op in right.reel}
    )


def glyph_authors(left: Tape, right: Tape) -> dict:
    fabric = confluence(left, right)
    counts: dict[str, int] = {}
    for strand in fabric.strands:
        if not strand.sheared:
            counts[strand.id.site] = (
                counts.get(strand.id.site, 0) + 1
            )
    return counts


def contributed_glyphs(tape: Tape) -> int:
    return sum(
        1
        for op in tape.reel
        if isinstance(op, Insert)
    )
