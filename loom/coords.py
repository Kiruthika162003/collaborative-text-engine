"""Coords: convert between a flat offset, a line and column, and a display column.

Text positions come in three coordinate systems and code that
touches text ends up translating between them constantly: the
flat character offset a slice uses, the line-and-column a human
speaks and an error message prints, and the display column a
terminal draws a caret at. This is the translation office for
all three over a plain string. Offset to line-and-column counts
the newlines before the offset and measures from the last one;
line-and-column back to offset sums the line lengths plus their
newlines and adds the column, and the two are exact inverses, a
round trip returning the offset it started from, which is the
property that lets code move between the systems without drift.
The display column is the third and the one the other modules
get wrong by assuming a character is a column: it measures the
line's text up to the column by display width, so a caret after
a tab or a wide glyph reports the cell a terminal would show it
at, not the character index. The conversions validate their
inputs against the actual text and refuse an offset past the
end or a column past its line's length with the shape of the
text named, because a coordinate out of bounds is a bug the
caller wants pointed at, not clamped into a plausible-looking
wrong answer. Columns and offsets are character-based except
the display column, which is the one place cells and characters
are deliberately, and namedly, different.
"""

from __future__ import annotations

from loom.columns import display_width
from loom.errors import Invalid, Missing


def offset_to_linecol(text: str, offset: int) -> tuple[int, int]:
    if not 0 <= offset <= len(text):
        raise Invalid(
            f"offset {offset} outside a {len(text)}-character text"
        )
    prefix = text[:offset]
    line = prefix.count("\n")
    column = offset - (prefix.rfind("\n") + 1)
    return (line, column)


def linecol_to_offset(text: str, line: int, column: int) -> int:
    lines = text.split("\n")
    if not 0 <= line < len(lines):
        raise Missing(f"line {line} of a {len(lines)}-line text")
    if not 0 <= column <= len(lines[line]):
        raise Missing(
            f"column {column} on a line of {len(lines[line])} character(s)"
        )
    before = sum(len(lines[number]) + 1 for number in range(line))
    return before + column


def display_column(text: str, offset: int, tab: int = 8) -> int:
    line, column = offset_to_linecol(text, offset)
    line_text = text.split("\n")[line]
    return display_width(line_text[:column], 0, tab)
