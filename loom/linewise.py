"""Linewise: the cloth read as lines, because humans point with two numbers.

The weave thinks in strands and the mailroom in ids, but a
person says line three, column seven, and this module is
the translation office. Lines are what newlines make them,
the split running on the visible cloth only, tombstoned
newlines dividing nothing, and every lookup answers with
the cloth's actual shape when refusing, line nine of a
five-line cloth being an error that should teach the
caller the territory rather than just the trespass. The
translation goes both ways: a line and column become the
single visible index every gesture wants, and a strand id
becomes the line it currently sits on, currently being
the honest word since lines are positions and positions
are weather. The typing helper rides on top so tests and
tools can speak human coordinates directly, one call from
line-and-column to operations on the wire.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.ids import OpId
from loom.weave import Op, Weave


def lines_of(weave: Weave) -> list[str]:
    return weave.text().split("\n")


def line_count(weave: Weave) -> int:
    return len(lines_of(weave))


def line_text(weave: Weave, line: int) -> str:
    held = lines_of(weave)
    if not 0 <= line < len(held):
        raise Missing(
            f"line {line} of a {len(held)}-line "
            "cloth; the territory, not just the "
            "trespass"
        )
    return held[line]


def visible_index(
    weave: Weave, line: int, column: int
) -> int:
    if column < 0:
        raise Invalid("columns start at zero")
    text = line_text(weave, line)
    if column > len(text):
        raise Missing(
            f"column {column} on a line of "
            f"{len(text)} glyph(s)"
        )
    held = lines_of(weave)
    index = sum(
        len(held[number]) + 1
        for number in range(line)
    )
    return index + column


def line_of(weave: Weave, strand_id: OpId) -> int:
    position = weave.by_id.get(strand_id)
    if position is None:
        raise Missing(
            f"{strand_id.wire()} is not in the fabric"
        )
    line = 0
    for strand in weave.strands[:position]:
        if not strand.sheared and strand.glyph == "\n":
            line += 1
    return line


def type_at_line(
    author: Author,
    line: int,
    column: int,
    text: str,
) -> list[Op]:
    index = visible_index(author.weave, line, column)
    return author.type_at(index, text)


def erase_at_line(
    author: Author,
    line: int,
    column: int,
    count: int,
) -> list[Op]:
    index = visible_index(author.weave, line, column)
    return author.erase_at(index, count)
