"""Wrap wide: wrap prose to a column measured in display cells, not characters.

The reflow module wraps to a width counted in characters,
which is right for Latin text and wrong the moment a line
holds wide glyphs, because a Chinese character fills two cells
and a line of them counted as characters wraps at twice the
intended column. This wraps to a width measured the columns
way, in the cells a terminal paints, so a paragraph of mixed
scripts breaks at the visual edge a reader sees rather than a
character count that drifts. It is otherwise reflow's greedy
rule: fill a line with as many words as fit, break before the
word that would overflow, and place a word wider than the
whole column alone on its own line rather than splitting it,
because splitting a word to meet a margin makes two broken
tokens where there was one whole one, the same principle
reflow keeps and for the same reason. Single newlines inside a
paragraph are soft wraps and become spaces, blank lines
between paragraphs are structure and are preserved, so the
wrapping rewraps prose and does not flatten a document's
shape. The width guard refuses a non-positive column, a page
one cell wide being a request that cannot be filled, and the
result is text, since where the wrapped text goes, a view or
an edit, is the caller's to decide.
"""

from __future__ import annotations

from loom.columns import display_width
from loom.errors import Invalid


def _wrap_paragraph(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current: list[str] = []
    current_width = 0
    for word in words:
        word_width = display_width(word)
        if current and current_width + 1 + word_width > width:
            lines.append(" ".join(current))
            current = [word]
            current_width = word_width
        else:
            current_width += (1 + word_width) if current else word_width
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def wrap_display(text: str, width: int) -> str:
    if width < 1:
        raise Invalid("a wrap column must be at least one cell wide")
    out: list[str] = []
    for block in text.split("\n\n"):
        joined = " ".join(block.split("\n"))
        out.append("\n".join(_wrap_paragraph(joined, width)))
    return "\n\n".join(out)


def fits_display(text: str, width: int) -> bool:
    return all(
        display_width(line) <= width for line in text.split("\n")
    )
