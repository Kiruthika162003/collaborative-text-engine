"""Indent: shift a block of lines left or right by editing their leading space.

Indenting a block is not a paragraph attribute; it is
inserting the same whitespace at the head of every line in
a range, and outdenting is shearing it back, so both are
runs of ordinary operations every replica weaves. The line
numbers stay valid throughout because neither indent nor
outdent touches a newline, only the spaces before the first
real glyph, so the operation can walk the range line by
line reading each line's live start without a plan going
stale under it. Two choices earn their keep. Indent leaves
blank lines alone, because indenting an empty line adds
trailing whitespace a reader cannot see and a linter will
flag, and a block indent that litters invisible spaces is
doing harm in the name of tidiness. Outdent removes only
leading whitespace and never a non-space glyph, and removes
at most one unit even from a line indented less than a full
unit, taking what is there rather than eating into the
text, because an outdent that deletes a letter to satisfy
its unit has mistaken the width for the content. The unit
must be actual whitespace and non-empty, since an indent of
zero width or of letters is not an indent at all, and it is
refused at the door rather than quietly doing nothing or
inserting prose.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.linewise import lines_of, visible_index
from loom.weave import Op


def _guard(author: Author, first: int, last: int, unit: str) -> None:
    if not unit or not unit.isspace():
        raise Invalid(
            "an indent unit must be non-empty whitespace; "
            "letters and zero width are not indentation"
        )
    held = lines_of(author.weave)
    if not 0 <= first <= last < len(held):
        raise Missing(
            f"lines {first}..{last} of a {len(held)}-line cloth"
        )


def indent_lines(
    author: Author, first: int, last: int, unit: str = "  "
) -> list[Op]:
    _guard(author, first, last, unit)
    held = lines_of(author.weave)
    ops: list[Op] = []
    for line in range(first, last + 1):
        if not held[line]:
            continue
        index = visible_index(author.weave, line, 0)
        ops.extend(author.type_at(index, unit))
    return ops


def _leading_spaces(text: str) -> int:
    return len(text) - len(text.lstrip())


def outdent_lines(
    author: Author, first: int, last: int, unit: str = "  "
) -> list[Op]:
    _guard(author, first, last, unit)
    ops: list[Op] = []
    for line in range(first, last + 1):
        text = lines_of(author.weave)[line]
        removable = min(_leading_spaces(text), len(unit))
        if removable == 0:
            continue
        index = visible_index(author.weave, line, 0)
        ops.extend(author.erase_at(index, removable))
    return ops
