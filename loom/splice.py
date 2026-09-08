"""The splice: replace as one gesture, because that is how hands think.

Nobody thinks delete six then insert five; they think
change quick to swift, and the splice is that thought made
operational: shear the stretch, type the replacement at
the same seam, one call returning one batch of operations.
The order inside the batch is shears first, and it matters
for the seam: the replacement anchors on the glyph left of
the stretch, not on anything being removed, so a
concurrent hand extending the old word finds its letters
beside the replacement rather than inside it, both
readable, neither eaten. The word-swap rides on top,
finding the first occurrence in the visible cloth and
splicing it, refusing when the cloth does not say the
word, and refusing wholesale the splice of nothing over
nothing, a gesture with no thought in it. What the splice
never promises is atomicity across the wire; the batch
travels as its operations, and remote fabrics may show
the seam mid-change, which is not a bug but what watching
someone edit looks like.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.weave import Op


def splice_at(
    author: Author,
    index: int,
    count: int,
    replacement: str,
) -> list[Op]:
    if count < 0:
        raise Invalid(
            "a negative stretch; the splice cannot "
            "remove what lies before its own seam"
        )
    if count == 0 and not replacement:
        raise Invalid(
            "a splice of nothing over nothing; a "
            "gesture with no thought in it"
        )
    ops: list[Op] = []
    if count:
        ops.extend(author.erase_at(index, count))
    if replacement:
        ops.extend(
            author.type_at(index, replacement)
        )
    return ops


def swap_word(
    author: Author, old: str, new: str
) -> list[Op]:
    if not old:
        raise Invalid(
            "swapping the empty word would match "
            "everywhere and mean nothing"
        )
    cloth = author.text()
    found = cloth.find(old)
    if found < 0:
        raise Missing(
            f"the cloth does not say {old!r}; "
            "nothing to swap"
        )
    return splice_at(author, found, len(old), new)
