"""Blockquotes: wrap and unwrap a run of lines in the greater-than markers.

Quoting a block is prefixing each of its lines with a
greater-than marker, and unquoting is shearing one marker
back, both runs of ordinary operations like the indent
module's, and like it neither touches a newline so the line
numbers stay valid as the operation walks the range. The one
decision that differs from indenting is blank lines: an
indent leaves them alone, but a blockquote must mark its
blank lines too, because an unmarked blank line ends the
quote in Markdown and a multi-paragraph quotation with a
bare gap in the middle silently splits into two quotes and a
paragraph. So quoting marks every line in the range, blank
ones included, to keep the quotation one unbroken block, and
that is the right call even though it writes a marker on a
line that shows nothing. Unquoting removes one level, the
marker and its following space if the space is there, and
never more than one level per call, because a nested quote
inside a quote is two separate quotings and collapsing both
at once would flatten a structure the writer built on
purpose. The depth of a line is read by counting its leading
markers, which is how a reader sees nesting, and a line with
no marker has depth zero, quoted by nobody.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Missing
from loom.linewise import lines_of, visible_index
from loom.weave import Op


def quote_depth(text: str) -> int:
    depth = 0
    rest = text
    while rest.startswith(">"):
        depth += 1
        rest = rest[1:]
        if rest.startswith(" "):
            rest = rest[1:]
    return depth


def _marker_length(text: str) -> int:
    if text.startswith("> "):
        return 2
    if text.startswith(">"):
        return 1
    return 0


def _guard(author: Author, first: int, last: int) -> None:
    held = lines_of(author.weave)
    if not 0 <= first <= last < len(held):
        raise Missing(
            f"lines {first}..{last} of a {len(held)}-line cloth"
        )


def quote_lines(author: Author, first: int, last: int) -> list[Op]:
    _guard(author, first, last)
    ops: list[Op] = []
    for line in range(first, last + 1):
        index = visible_index(author.weave, line, 0)
        ops.extend(author.type_at(index, "> "))
    return ops


def unquote_lines(author: Author, first: int, last: int) -> list[Op]:
    _guard(author, first, last)
    ops: list[Op] = []
    for line in range(first, last + 1):
        text = lines_of(author.weave)[line]
        length = _marker_length(text)
        if length == 0:
            continue
        index = visible_index(author.weave, line, 0)
        ops.extend(author.erase_at(index, length))
    return ops


def quoted_lines(author: Author) -> set[int]:
    return {
        number
        for number, text in enumerate(lines_of(author.weave))
        if quote_depth(text) >= 1
    }
