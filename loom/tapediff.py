"""Tape diff: what two recordings hold that the other does not, by identity.

Two tapes of the same document that drifted apart can be
compared without replaying either: because every operation
carries a globally unique id, the difference is set
arithmetic on the ids, the operations only the left tape
holds, only the right, and the shared spine both agree on.
This is the question a sync planner asks before a handshake
and the question a reviewer asks after one, and answering
it by id rather than by text means a reordering that
produced identical text is correctly reported as no
difference, while two genuinely divergent edits are named
even if they happen to read alike. The summary counts the
three regions, and the per-site breakdown of the
divergence says which hands did the diverging, because
when two tapes disagree the first useful question is whose
operations are the ones in question. A pair of identical
tapes reports a clean spine and empty wings, the honest
shape of agreement.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.transcript import Tape
from loom.weave import Insert


@dataclass(frozen=True)
class TapeDiff:
    only_left: list
    only_right: list
    shared: list


def diff(left: Tape, right: Tape) -> TapeDiff:
    left_ids = {op.id: op for op in left.reel}
    right_ids = {op.id: op for op in right.reel}
    only_left = [
        op
        for op in left.reel
        if op.id not in right_ids
    ]
    only_right = [
        op
        for op in right.reel
        if op.id not in left_ids
    ]
    shared = [
        op
        for op in left.reel
        if op.id in right_ids
    ]
    return TapeDiff(
        only_left=only_left,
        only_right=only_right,
        shared=shared,
    )


def divergence_by_site(
    left: Tape, right: Tape
) -> dict[str, int]:
    result = diff(left, right)
    counts: dict[str, int] = {}
    for op in result.only_left + result.only_right:
        counts[op.id.site] = (
            counts.get(op.id.site, 0) + 1
        )
    return counts


def _glyphs(ops: list) -> int:
    return sum(
        1 for op in ops if isinstance(op, Insert)
    )


def report(left: Tape, right: Tape) -> str:
    result = diff(left, right)
    if not result.only_left and not result.only_right:
        return (
            f"identical tapes; a shared spine of "
            f"{len(result.shared)}, no divergence"
        )
    lines = [
        f"shared spine {len(result.shared)}, "
        f"{len(result.only_left)} only left, "
        f"{len(result.only_right)} only right"
    ]
    for site, count in sorted(
        divergence_by_site(left, right).items()
    ):
        lines.append(
            f"  {site} diverged by {count} operation(s)"
        )
    lines.append(
        "compared by identity; a reorder that reads "
        "alike is correctly no difference"
    )
    return "\n".join(lines)
