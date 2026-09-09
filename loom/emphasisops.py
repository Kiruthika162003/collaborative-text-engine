"""Emphasis ops: wrap a range in Markdown markers, as text every reader already understands.

The marks module records emphasis as a metadata layer over
the strands, which is right when the emphasis must survive as
structured data; this does the other thing, writing the
Markdown markers into the text itself, so the emphasis
travels as plain characters a reader, a renderer, and a
paste into any other editor all understand without the mark
layer coming along. Wrapping a range is inserting the marker
before its first glyph and after its last, minted as
operations from the far end back so the closing marker's
insertion does not shift the position the opening marker
still needs. The four markers are the ones a writing room
types, two stars for bold, one for italic, a backtick for
code, two tildes for strike, and each is its own verb so a
caller says what it means. The honest boundary with the mark
layer is stated: this writes literal characters, so wrapping
a range that already carries the same markers doubles them,
and the module does not check, because whether a second bold
is a mistake or a deliberate nesting is the caller's call and
not something a wrapper should decide by refusing. What it
does guarantee is that the markers are real operations every
replica weaves, so bold typed on one screen is bold on all of
them, not a private rendering one editor sees.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Invalid
from loom.weave import Op


def wrap(author: Author, start: int, count: int, marker: str) -> list[Op]:
    if count < 1:
        raise Invalid("wrapping zero glyphs emphasizes nothing")
    end = start + count
    author.weave.strand_at_visible(end - 1)
    ops = author.type_at(end, marker)
    ops.extend(author.type_at(start, marker))
    return ops


def bold(author: Author, start: int, count: int) -> list[Op]:
    return wrap(author, start, count, "**")


def italic(author: Author, start: int, count: int) -> list[Op]:
    return wrap(author, start, count, "*")


def code(author: Author, start: int, count: int) -> list[Op]:
    return wrap(author, start, count, "`")


def strike(author: Author, start: int, count: int) -> list[Op]:
    return wrap(author, start, count, "~~")
