"""Patch: make the document read like a target text, changing only what differs.

Sometimes an edit arrives as a whole new version of the text
rather than as operations, a file reformatted by a tool, a
paragraph rewritten offline, and the document has to be
brought to match it. The lazy way is to shear everything and
retype the target, which converges but throws away the
identity of every unchanged glyph and every anchor riding it,
so a comment on a word that never changed follows the deleted
text into oblivion. This does the careful thing instead: it
diffs the current text against the target, keeps the runs
that match untouched with their strands intact, and mints
operations only for the runs that differ, a delete where the
target dropped text, an insert where it added, a replace for
a stretch that changed. The strand ids of the changing runs
are read before any operation is minted and each glyph's live
position is recomputed as it is reached, the guard the replace
and case operations keep, so the shifting the edits cause does
not send a later change to the wrong place. The diff is the
one the standard library computes, minimal enough for the
job and not claimed to be globally optimal, which is the
honest bound: it will occasionally split a change into two
runs a human would have seen as one, and that costs a little
identity at the seam but never correctness, since the result
is the target text exactly, by construction.
"""

from __future__ import annotations

import difflib

from loom.author import Author
from loom.weave import Op


def patch(author: Author, target: str) -> list[Op]:
    current = author.text()
    ids = [
        author.weave.strand_at_visible(index).id
        for index in range(len(current))
    ]

    def live_index(original: int) -> int:
        if original >= len(ids):
            return author.weave.visible_count()
        position = author.weave.by_id[ids[original]]
        return sum(
            1
            for strand in author.weave.strands[:position]
            if not strand.sheared
        )

    matcher = difflib.SequenceMatcher(a=current, b=target, autojunk=False)
    ops: list[Op] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag in {"delete", "replace"}:
            for original in range(i1, i2):
                ops.extend(author.erase_at(live_index(original), 1))
        if tag in {"insert", "replace"}:
            ops.extend(author.type_at(live_index(i2), target[j1:j2]))
    return ops


def would_change(author: Author, target: str) -> bool:
    return author.text() != target
