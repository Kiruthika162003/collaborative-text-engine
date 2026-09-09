"""Align: line up a block of lines on a shared delimiter by inserting padding.

Columns of assignments or definitions read better when their
equals signs or colons line up, and this does that by finding
the delimiter in each line of a range and inserting spaces
before it until they all sit at the same column, the furthest
right any of them started. It is padding only, spaces woven
in before the delimiter, so no character a writer typed moves
except to the right, and the alignment is expressed as
operations every replica weaves, so the aligned columns are
the document's, not one editor's rendering. Two honest limits
are stated. It aligns on the first occurrence of the
delimiter in each line, because aligning on a later one would
need to know which the writer meant and it cannot, so the
first is the predictable choice. And a line in the range with
no delimiter is left exactly as it is rather than forced into
the column, because a line that does not participate in the
alignment is not misaligned, it is just a different kind of
line, and shoving it rightward would be inventing structure.
A block already aligned mints nothing, since every line's
delimiter already sits at the target column and there is no
padding to add, which lets an alignment run on every save
without churning a document that was already tidy.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.linewise import lines_of, visible_index
from loom.weave import Op


def align(
    author: Author, first: int, last: int, delimiter: str
) -> list[Op]:
    if not delimiter:
        raise Invalid("alignment needs a delimiter to line up on")
    lines = lines_of(author.weave)
    if not 0 <= first <= last < len(lines):
        raise Missing(
            f"lines {first}..{last} of a {len(lines)}-line cloth"
        )
    positions = {}
    for line_no in range(first, last + 1):
        at = lines[line_no].find(delimiter)
        if at >= 0:
            positions[line_no] = at
    if not positions:
        return []
    target = max(positions.values())
    ops: list[Op] = []
    for line_no, column in positions.items():
        pad = target - column
        if pad <= 0:
            continue
        index = visible_index(author.weave, line_no, column)
        ops.extend(author.type_at(index, " " * pad))
    return ops


def aligned_column(
    author: Author, first: int, last: int, delimiter: str
) -> int:
    lines = lines_of(author.weave)
    columns = [
        lines[line_no].find(delimiter)
        for line_no in range(first, last + 1)
        if delimiter in lines[line_no]
    ]
    return max(columns, default=-1)
