"""Edit cost: how far apart two drafts are, in the operations that separate them.

Two texts can be close in meaning and far in edits or the
reverse, and edit cost measures the second honestly: the
Levenshtein distance, the fewest single-character
insertions, deletions, and substitutions that turn one text
into the other. The loom uses this not to grade prose but to
size a sync, because the distance between a replica's text
and the truth is a lower bound on how many operations must
cross to reconcile them, and a lower bound is exactly what
a scheduler wants before committing bandwidth. The
computation is the classic dynamic-programming table kept
to two rows rather than the full grid, because a document
is long and the full grid is its length squared in memory
for a number that needs only the previous row to compute,
and a primitive that runs out of memory on real input is a
primitive for toy input. Similarity is one minus distance
over the longer length, a number in the unit interval for
sorting revisions, and identical texts cost zero, the one
answer the whole edifice must get right or nothing above it
can be trusted.
"""

from __future__ import annotations


def distance(old: str, new: str) -> int:
    if old == new:
        return 0
    if not old:
        return len(new)
    if not new:
        return len(old)
    previous = list(range(len(new) + 1))
    for i, old_char in enumerate(old, start=1):
        current = [i]
        for j, new_char in enumerate(new, start=1):
            cost = 0 if old_char == new_char else 1
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + cost,
                )
            )
        previous = current
    return previous[-1]


def similarity(old: str, new: str) -> float:
    if not old and not new:
        return 1.0
    longer = max(len(old), len(new))
    return round(1 - distance(old, new) / longer, 3)


def sync_lower_bound(old: str, new: str) -> str:
    d = distance(old, new)
    return (
        f"at least {d} operation(s) must cross to "
        "reconcile these; a lower bound is what a "
        "scheduler wants before committing bandwidth"
    )
