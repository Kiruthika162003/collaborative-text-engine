"""Three-way merge: a base and two edits reconciled the way the CRDT would.

Two people who forked a document from the same base and
edited offline can be reconciled by their operations, and
confluence already does that; but sometimes all that
survives is text, three plain strings, base and ours and
theirs, and this module merges those the honest way a
diff3 does, aligning both sides against the base and
taking the non-conflicting changes from each. Where the
two sides changed the same base region differently, the
merge does not guess: it emits a conflict block naming
both versions, because a three-way merge that silently
picks a side is the tool everyone learns to distrust after
it eats their afternoon once. Regions only one side
touched are taken from that side, regions neither touched
are kept, and identical changes from both sides collapse
to one, since two people typing the same fix is agreement,
not conflict. The result reports whether it is clean, and
the conflict count is the number a caller checks before
shipping the merge unread.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True)
class MergeResult:
    text: str
    conflicts: int

    def is_clean(self) -> bool:
        return self.conflicts == 0


def _opcodes(base: list[str], side: list[str]):
    return SequenceMatcher(
        a=base, b=side, autojunk=False
    ).get_opcodes()


def _changes(base: list[str], side: list[str]) -> dict:
    edits = {}
    for verb, i0, i1, j0, j1 in _opcodes(base, side):
        if verb != "equal":
            edits[(i0, i1)] = side[j0:j1]
    return edits


def merge(
    base_text: str, ours_text: str, theirs_text: str
) -> MergeResult:
    base = base_text.split("\n")
    ours = _changes(base, ours_text.split("\n"))
    theirs = _changes(base, theirs_text.split("\n"))

    out: list[str] = []
    conflicts = 0
    index = 0
    spans = sorted(set(ours) | set(theirs))
    for start, end in spans:
        out.extend(base[index:start])
        in_ours = ours.get((start, end))
        in_theirs = theirs.get((start, end))
        if in_ours is not None and in_theirs is not None:
            if in_ours == in_theirs:
                out.extend(in_ours)
            else:
                conflicts += 1
                out.append("<<<<<<< ours")
                out.extend(in_ours)
                out.append("=======")
                out.extend(in_theirs)
                out.append(">>>>>>> theirs")
        elif in_ours is not None:
            out.extend(in_ours)
        else:
            out.extend(in_theirs)
        index = end
    out.extend(base[index:])
    return MergeResult(
        text="\n".join(out), conflicts=conflicts
    )
