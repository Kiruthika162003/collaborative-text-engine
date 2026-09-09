"""Renumber: fix an ordered list's typed numbers in the document, not just in a view.

The lists module reads a list and renders it with the
numbers corrected, but the rendering is a view; the document
still holds the wrong digits a writer typed, and two replicas
looking at the same view still disagree about the text
underneath. This closes that gap by minting the operations
that make the correction real: for each numbered item whose
typed number is wrong, it shears the stale digits and weaves
the right ones in their place, so the document itself carries
the corrected sequence and every replica converges on it.
The discipline is to touch only what is wrong. An item
already bearing the right number is left with its digits and
their identities intact, a bullet is never touched because
bullets carry no number to fix, and a run that is already
correctly numbered mints nothing, so a formatter can renumber
on every save without churning a tidy list. The numbering
follows the same rules the lists module reads by, restarting
at each nesting depth and at each break where a paragraph
splits one list into two, so renumbering a document with
nested lists produces the counts a reader expects rather than
one long sequence flowing through everything. The correction
is confined to the digits; the item's text and its leading
indentation are never disturbed, because renumbering fixes
the number and nothing else is its business.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.linewise import lines_of, visible_index
from loom.weave import Op

BULLET = re.compile(r"^( *)- ")
NUMBERED = re.compile(r"^( *)(\d+)\. ")


def _plan(author: Author) -> list[tuple[int, int, int, int]]:
    counters: dict[int, int] = {}
    plan: list[tuple[int, int, int, int]] = []
    for line_no, raw in enumerate(lines_of(author.weave)):
        bullet = BULLET.match(raw)
        numbered = NUMBERED.match(raw)
        if bullet is None and numbered is None:
            counters.clear()
            continue
        indent = (bullet or numbered).group(1)
        depth = len(indent) // 2
        for deeper in list(counters):
            if deeper > depth:
                del counters[deeper]
        counters[depth] = counters.get(depth, 0) + 1
        if numbered is not None:
            typed = int(numbered.group(2))
            correct = counters[depth]
            if typed != correct:
                plan.append(
                    (line_no, len(indent), len(numbered.group(2)), correct)
                )
    return plan


def needs_renumber(author: Author) -> bool:
    return bool(_plan(author))


def renumber(author: Author) -> list[Op]:
    ops: list[Op] = []
    for line_no, column, typed_length, correct in _plan(author):
        index = visible_index(author.weave, line_no, column)
        ops.extend(author.erase_at(index, typed_length))
        ops.extend(author.type_at(index, str(correct)))
    return ops
