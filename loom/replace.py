"""Replace: find every occurrence and rewrite it as honest operations.

Search-and-replace in a collaborative document cannot be a
string substitution on the text, because the text is a view
and the truth is the weave; a replace must find each
occurrence's strands and mint the shears and inserts that
turn them into the replacement, exactly as a human retyping
would. This finds all non-overlapping occurrences in one
pass left to right, then rewrites them, and the ordering
matters: it resolves every occurrence's strand ids before
minting anything, because minting shifts visible positions
and a plan built on positions mid-rewrite corrects itself
into corruption. Each occurrence becomes a run of shears
over its old glyphs and a run of inserts anchored at the
seam, the same seam discipline the splice uses, so a
concurrent edit inside a replaced occurrence survives as a
tombstone-anchored fragment rather than vanishing. Replace
of a term not present mints nothing and says so, because a
no-op that reports success teaches callers to trust a lie,
and replacing a term with itself is refused as the busywork
it is.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.errors import Invalid
from loom.weave import Op


@dataclass
class ReplaceResult:
    occurrences: int
    ops: list[Op]


def _find_all(text: str, needle: str) -> list[int]:
    starts = []
    at = text.find(needle)
    while at >= 0:
        starts.append(at)
        at = text.find(needle, at + len(needle))
    return starts


def replace_all(
    author: Author, needle: str, replacement: str
) -> ReplaceResult:
    if not needle:
        raise Invalid(
            "an empty needle matches between every "
            "letter; replace needs something to find"
        )
    if needle == replacement:
        raise Invalid(
            "replacing a term with itself is busywork "
            "wearing a gesture"
        )
    text = author.text()
    starts = _find_all(text, needle)
    if not starts:
        return ReplaceResult(occurrences=0, ops=[])
    targets = []
    for start in starts:
        ids = [
            author.weave.strand_at_visible(
                start + offset
            ).id
            for offset in range(len(needle))
        ]
        targets.append((start, ids))
    minted: list[Op] = []
    shift = 0
    for start, ids in targets:
        anchor_index = start + shift
        for strand_id in ids:
            position = author.weave.by_id[strand_id]
            visible = sum(
                1
                for s in author.weave.strands[:position]
                if not s.sheared
            )
            minted.extend(
                author.erase_at(visible, 1)
            )
        if replacement:
            minted.extend(
                author.type_at(
                    anchor_index, replacement
                )
            )
        shift += len(replacement) - len(needle)
    return ReplaceResult(
        occurrences=len(starts), ops=minted
    )
