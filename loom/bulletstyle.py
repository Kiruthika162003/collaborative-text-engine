"""Bullet style: unify a document's bullet markers to one character, as operations.

Markdown accepts three bullet characters, the dash, the star,
and the plus, and a document written by several hands ends up
mixing them, which renders fine but reads as carelessness and
trips a linter tuned to one. This normalizes them to a chosen
marker, replacing each bullet line's marker character with
the one the caller wants, as operations every replica weaves.
The change is exactly one character per line and nothing else:
the indentation that sets a bullet's nesting is preserved, the
space after the marker is preserved, and the item's text is
untouched, because normalizing style should never move a word.
The line-leading position is what makes a marker a bullet, so
a star that opens a list item is changed while a star that
emphasizes a word mid-sentence is not, since the emphasis star
is not at the head of a line with a space after it and the
pattern that catches bullets does not catch it. A line already
carrying the chosen marker is left with its strand intact
rather than rewritten to the same character, so running the
normalizer twice is a no-op and it can be run on every save,
and because each replacement is one character for one
character the positions never shift, which keeps the whole
pass simple and its result identical on every machine.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.errors import Invalid
from loom.linewise import lines_of, visible_index
from loom.weave import Op

BULLET = re.compile(r"^(\s*)([-*+])(\s+)(.*)$")
MARKERS = "-*+"


def normalize_bullets(author: Author, marker: str = "-") -> list[Op]:
    if marker not in MARKERS:
        raise Invalid(
            f"{marker!r} is not a bullet marker; use one of {MARKERS!r}"
        )
    ops: list[Op] = []
    for line_no, raw in enumerate(lines_of(author.weave)):
        match = BULLET.match(raw)
        if match is None or match.group(2) == marker:
            continue
        column = len(match.group(1))
        index = visible_index(author.weave, line_no, column)
        ops.extend(author.erase_at(index, 1))
        ops.extend(author.type_at(index, marker))
    return ops


def bullet_markers(author: Author) -> set[str]:
    found = set()
    for raw in lines_of(author.weave):
        match = BULLET.match(raw)
        if match is not None:
            found.add(match.group(2))
    return found


def is_uniform(author: Author) -> bool:
    return len(bullet_markers(author)) <= 1
