"""Sort lines: reorder a block, which a sequence CRDT can only do by rewriting it.

Sorting lines is the one common editor gesture the weave
cannot do gently. Every other operation here shears or
inserts a few strands and leaves the rest with their
identities intact, but reordering is a permutation, and a
sequence CRDT has no move: the only way to put line three
above line one is to shear the block and weave it back in
the new order, so sorting replaces the identities of every
line in the range. This module does exactly that and says
so, rather than pretending a sort is a light touch, because
a comment anchored to a line inside the sorted range will
not follow it and a caller needs to know that before running
a sort under someone else's cursor. The honest compensations
are two. A range already in order is a no-op that mints
nothing and returns empty, so a formatter can sort on every
save without churning a document that was already sorted, and
the rewrite is confined to the exact range asked for, the
lines above and below it untouched with their strands and
anchors intact. The comparison is plain string order, with a
reverse flag, and the caller chooses the range, because a
sort that guessed which lines the writer meant would sort the
wrong ones, and the wrong lines sorted is worse than no sort.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Missing
from loom.linewise import lines_of, visible_index
from loom.weave import Op


def _guard(author: Author, first: int, last: int) -> None:
    held = lines_of(author.weave)
    if not 0 <= first <= last < len(held):
        raise Missing(
            f"lines {first}..{last} of a {len(held)}-line cloth"
        )


def is_sorted(
    author: Author, first: int, last: int, reverse: bool = False
) -> bool:
    _guard(author, first, last)
    block = lines_of(author.weave)[first : last + 1]
    return block == sorted(block, reverse=reverse)


def sort_lines(
    author: Author, first: int, last: int, reverse: bool = False
) -> list[Op]:
    _guard(author, first, last)
    held = lines_of(author.weave)
    block = held[first : last + 1]
    ordered = sorted(block, reverse=reverse)
    if ordered == block:
        return []
    start = visible_index(author.weave, first, 0)
    end = visible_index(author.weave, last, len(held[last]))
    ops = author.erase_at(start, end - start)
    ops.extend(author.type_at(start, "\n".join(ordered)))
    return ops
