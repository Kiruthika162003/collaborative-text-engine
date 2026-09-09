"""Boxes: frame text in an ASCII border, aligned by the width a terminal shows.

A callout or a banner reads better boxed, and this draws the
frame around one or many lines, sizing the box to its widest
line and padding the rest to match so the right border forms a
straight edge. The width is measured the columns way, by
display cells, so a box around text holding a wide glyph, a
Chinese character that paints two cells, has a border that
lines up rather than one that juts a cell short, which is the
whole point of a box and the thing a naive glyph-count border
gets wrong. The border is ASCII, the plus and dash and
pipe, deliberately, because ASCII survives every terminal and
encoding where the prettier box-drawing characters turn to
mojibake on the one machine that matters, and a portable box
that is a little plain beats a handsome one that breaks. The
padding inside the frame is the caller's, one space by
default, and multi-line text is framed as the block it is,
each line padded to the common inner width so the box is a
rectangle whatever the ragged lengths inside it. It is pure
rendering that returns a string; it weaves nothing, because a
box drawn around text is a way of showing the text, not a
change to it, and baking borders into a document would corrupt
the content the moment anyone edited near them.
"""

from __future__ import annotations

from loom.columns import display_width, pad_to


def box(text: str, padding: int = 1) -> str:
    lines = text.split("\n")
    inner = max((display_width(line) for line in lines), default=0) + padding * 2
    border = "+" + "-" * inner + "+"
    pad = " " * padding
    body = [f"|{pad_to(pad + line, inner)}|" for line in lines]
    return "\n".join([border, *body, border])


def banner(text: str, padding: int = 1) -> str:
    return box(text, padding)
