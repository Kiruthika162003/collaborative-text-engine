"""Ellipses: turn a run of exactly three dots into the ellipsis character, as operations.

Three dots typed in a row are an ellipsis, and rendering them
as the single ellipsis character rather than three periods
gives typographers what they want and, more usefully in a
collaborative editor, makes the ellipsis one glyph a caret
cannot land in the middle of, where three separate periods
invite an edit that splits the mark. This converts a run of
exactly three dots, expressed as a patch so only those three
characters change and the rest of the text keeps its strands.
The precision is the point: it matches three dots that are not
part of a longer run, so four dots, which a writer uses to
mean a trailing-off with a full stop, and two dots, which are
usually a typo the writer will fix another way, are both left
alone rather than swept into an ellipsis the writer did not
mean. It touches dots only and no other punctuation, in
particular leaving hyphens and dashes entirely to themselves,
because dash conversion is a separate decision with its own
ambiguities and folding it in here would surprise a caller who
asked only about dots. Converting back is not offered, because
the ellipsis character is the canonical form and a document
that reached it has no reason to walk back to three periods.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.patch import patch
from loom.weave import Op

ELLIPSIS = chr(0x2026)
THREE_DOTS = re.compile(r"(?<!\.)\.{3}(?!\.)")


def normalized_text(text: str) -> str:
    return THREE_DOTS.sub(ELLIPSIS, text)


def normalize(author: Author) -> list[Op]:
    return patch(author, normalized_text(author.text()))


def has_three_dots(text: str) -> bool:
    return THREE_DOTS.search(text) is not None
