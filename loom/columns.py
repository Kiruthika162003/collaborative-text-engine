"""Columns: the visual width of text, which is not its glyph count.

Linewise counts columns as glyphs, one glyph one column,
and for plain Latin prose that is right. It is wrong the
moment the text holds a wide glyph, a Chinese character or
a fullwidth form that a terminal paints two cells across,
or a combining mark that paints none of its own because it
rides the glyph before it, or a tab that jumps to the next
stop rather than advancing one. This module is the second
opinion linewise cannot give: the display width of a run,
the visual column a caret sits at, and the glyph index a
visual column lands on, all measured in the cells a
fixed-width terminal would actually use. The first guess
was that width and length differ only for the exotic and a
document could ignore the gap; the trials refuted it, an
alignment built on glyph counts tearing the instant a
single wide glyph entered a column of otherwise Latin text,
so the gap is measured here rather than assumed away. The
measure follows the East Asian width property for the wide
and fullwidth glyphs, treats zero-width and combining marks
as the zero they are, expands tabs to a caller's stop, and
counts everything else as the one cell it takes, which is
not the whole truth of every terminal's font but is the
truth the common ones agree on.
"""

from __future__ import annotations

import unicodedata

from loom.errors import Invalid

DEFAULT_TAB = 8


def glyph_width(glyph: str, column: int = 0, tab: int = DEFAULT_TAB) -> int:
    if glyph == "\t":
        if tab <= 0:
            raise Invalid("a tab stop of zero has no next stop")
        return tab - (column % tab)
    if glyph == "\n":
        return 0
    if unicodedata.combining(glyph):
        return 0
    category = unicodedata.category(glyph)
    if category in {"Mn", "Me", "Cf"}:
        return 0
    if unicodedata.east_asian_width(glyph) in {"W", "F"}:
        return 2
    return 1


def display_width(text: str, start: int = 0, tab: int = DEFAULT_TAB) -> int:
    column = start
    for glyph in text:
        column += glyph_width(glyph, column, tab)
    return column - start


def visual_column(text: str, glyph_index: int, tab: int = DEFAULT_TAB) -> int:
    if not 0 <= glyph_index <= len(text):
        raise Invalid(
            f"glyph index {glyph_index} on a line of "
            f"{len(text)} glyph(s)"
        )
    return display_width(text[:glyph_index], 0, tab)


def glyph_at_column(text: str, target: int, tab: int = DEFAULT_TAB) -> int:
    if target < 0:
        raise Invalid("visual columns start at zero")
    column = 0
    for index, glyph in enumerate(text):
        width = glyph_width(glyph, column, tab)
        if target < column + width:
            return index
        column += width
    return len(text)


def pad_to(text: str, target: int, tab: int = DEFAULT_TAB) -> str:
    width = display_width(text, 0, tab)
    if width >= target:
        return text
    return text + " " * (target - width)


def is_wide(glyph: str) -> bool:
    return glyph_width(glyph) == 2
