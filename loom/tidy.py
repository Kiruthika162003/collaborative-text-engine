"""Tidy: run the safe formatters in one pass, returning the operations they minted.

The individual formatters each fix one mechanical flaw; tidy
runs the safe ones in a sensible order and hands back the
combined operations, so a caller cleans a document with one
call rather than five. The order is chosen so the passes do
not undo each other: expand tabs first, since a tab's width
affects the columns the later passes see, then trim trailing
whitespace, unify the bullet markers, renumber the ordered
lists, and finally collapse the blank-line runs. What tidy
includes is exactly the fixes that are unambiguous, the ones
whose right answer a tool can know: whitespace a reader cannot
see, a tab that should be spaces, a bullet character that
should match its neighbours, a list number that should follow
its predecessor, a blank run past the limit. What it leaves
alone is stated and deliberate: it does not touch a heading
that skipped a level, because promoting or demoting it is a
decision about the document's structure that only the writer
can make, and it does not balance brackets or resolve
conflict markers, because those need a human to say which side
is right. So tidy is the trustworthy half of formatting, the
part safe to run on every save, and the judgement calls are
left to the writer and the linter that names them.
"""

from __future__ import annotations

from loom.author import Author
from loom.blanklines import collapse_blanks
from loom.bulletstyle import normalize_bullets
from loom.renumber import renumber
from loom.tabs import expand_tabs
from loom.weave import Op
from loom.whitespace import trim_trailing


def tidy(
    author: Author,
    bullet: str = "-",
    tab_width: int = 4,
    max_blanks: int = 1,
) -> list[Op]:
    ops: list[Op] = []
    ops.extend(expand_tabs(author, tab_width))
    ops.extend(trim_trailing(author))
    ops.extend(normalize_bullets(author, bullet))
    ops.extend(renumber(author))
    ops.extend(collapse_blanks(author, max_blanks))
    return ops
