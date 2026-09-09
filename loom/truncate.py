"""Truncate: shorten text to a budget without cutting a word in half where it can help it.

Shortening a string to fit a label or a preview is easy to
do badly: slice at the character count and a word is
guillotined mid-syllable. This backs off to the last word
boundary inside the budget instead, so the cut lands between
words and the ellipsis reads as an omission rather than a
mangling, and it only cuts inside a word when the first word
is already longer than the whole budget, where there is no
boundary to retreat to and a hard cut is the honest option.
The ellipsis counts against the budget, because a truncation
that returns more characters than it was asked for has not
truncated, and a budget smaller than the ellipsis returns a
clipped ellipsis rather than overrunning. A width-aware
variant measures the budget in display columns rather than
characters, using the same rule that lets a wide glyph count
as the two cells it paints, so a label truncated to twenty
columns is twenty columns whether it holds Latin or Chinese.
The middle variant keeps the head and the tail and drops the
centre, which is what a path or a long identifier wants,
since the ends carry the identity and the middle is the part
a reader skips. None of the three pads: a string shorter than
its budget is returned exactly as it is, because padding is a
different job with a different name.
"""

from __future__ import annotations

from loom.columns import display_width, glyph_at_column
from loom.errors import Invalid

ELLIPSIS = "..."


def _guard(limit: int) -> None:
    if limit < 0:
        raise Invalid("a truncation budget cannot be negative")


def truncate(text: str, limit: int, ellipsis: str = ELLIPSIS) -> str:
    _guard(limit)
    if len(text) <= limit:
        return text
    if limit <= len(ellipsis):
        return ellipsis[:limit]
    budget = limit - len(ellipsis)
    head = text[:budget]
    if text[budget] == " ":
        return head.rstrip() + ellipsis
    space = head.rfind(" ")
    if space > 0:
        return head[:space].rstrip() + ellipsis
    return head + ellipsis


def truncate_width(text: str, limit: int, ellipsis: str = ELLIPSIS) -> str:
    _guard(limit)
    if display_width(text) <= limit:
        return text
    ellipsis_width = display_width(ellipsis)
    if limit <= ellipsis_width:
        return ellipsis[: max(limit, 0)]
    budget = limit - ellipsis_width
    cut = glyph_at_column(text, budget)
    head = text[:cut]
    if cut < len(text) and text[cut] == " ":
        return head.rstrip() + ellipsis
    space = head.rfind(" ")
    if space > 0:
        return head[:space].rstrip() + ellipsis
    return head + ellipsis


def middle_truncate(text: str, limit: int, ellipsis: str = ELLIPSIS) -> str:
    _guard(limit)
    if len(text) <= limit:
        return text
    if limit <= len(ellipsis):
        return ellipsis[:limit]
    keep = limit - len(ellipsis)
    head_len = keep // 2
    tail_len = keep - head_len
    return text[:head_len] + ellipsis + text[len(text) - tail_len :]
