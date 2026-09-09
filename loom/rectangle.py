"""Rectangle: slice and drop vertical columns of text, the block a column selection takes.

Fixed-width data and aligned tables sometimes want a vertical
cut, a column of characters taken from every line at once, the
block an editor's column selection grabs. This does that
across the whole text: slicing keeps the characters in a
column range from each line, dropping removes them, and the
single-column helper reads one character down a position. The
basis is the character index, not the display column, and that
is stated because it matters at exactly the place display
width usually matters: a line with a wide glyph before the cut
has its columns land a character earlier than a terminal would
show, so this is the right tool for fixed-width ASCII data and
the wrong one for a table holding wide glyphs, which wants the
columns module's display measure instead. Short lines
contribute only the characters they have rather than being
padded to the cut, because a line that ends before the column
has nothing there to take and inventing spaces would put
content in the block that the line never held. The operations
are pure text returning strings, since a rectangular edit as
convergent operations is a harder problem than the extraction,
and separating the reading of a block from the writing of one
keeps the reading simple and honest about what it is.
"""

from __future__ import annotations


def slice_columns(text: str, left: int, right: int) -> str:
    return "\n".join(line[left:right] for line in text.split("\n"))


def drop_columns(text: str, left: int, right: int) -> str:
    return "\n".join(
        line[:left] + line[right:] for line in text.split("\n")
    )


def column(text: str, index: int) -> str:
    return "".join(
        line[index] for line in text.split("\n") if index < len(line)
    )


def widest(text: str) -> int:
    return max((len(line) for line in text.split("\n")), default=0)
