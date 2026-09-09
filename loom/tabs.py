"""Tabs: expand tab characters to spaces at their visual stops, as operations.

A tab is a visual instruction, jump to the next stop, not a
fixed number of spaces, so expanding one correctly means
knowing the column it sits at: a tab at column zero fills to
the first stop, a tab already three columns in fills only the
one space left to reach a four-column stop. This expands them
that way, walking each line and counting columns by display
width so a tab after a wide glyph, which paints two cells,
lands on the right stop rather than two short. The expansion
is expressed as a patch against the target text, so it reuses
the diffing machinery that changes only what differs and
leaves the untouched runs' strands intact, and it converges
across replicas for the same reason a patch does. Only the
one direction is offered, tabs to spaces, because it is the
safe and common one; the reverse, spaces back to tabs, is
lossy, since it cannot know which runs of spaces were a tab
and which were spaces a writer meant, and a tool that guessed
would turn alignment into tabs that realign differently under
another width. The stop width is the caller's, defaulting to
four, because there is no universal tab width and pretending
one exists is how a document looks ragged in the next
editor.
"""

from __future__ import annotations

from loom.author import Author
from loom.columns import glyph_width
from loom.patch import patch
from loom.weave import Op


def _expand_line(line: str, width: int) -> str:
    out: list[str] = []
    column = 0
    for glyph in line:
        if glyph == "\t":
            spaces = glyph_width("\t", column, width)
            out.append(" " * spaces)
            column += spaces
        else:
            out.append(glyph)
            column += glyph_width(glyph, column, width)
    return "".join(out)


def expanded_text(text: str, width: int = 4) -> str:
    return "\n".join(_expand_line(line, width) for line in text.split("\n"))


def expand_tabs(author: Author, width: int = 4) -> list[Op]:
    return patch(author, expanded_text(author.text(), width))


def has_tabs(text: str) -> bool:
    return "\t" in text
