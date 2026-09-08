"""Smart quotes: straight quotes curled by context, with the guesses it gets wrong named.

Curling quotes is deciding, for each straight mark, whether
it opens or closes, and the decision is a heuristic on the
character before it: a quote after a space or an opening
bracket opens, a quote after a letter closes, an apostrophe
between letters is a right single quote. That rule is right
most of the time and this module applies it as the casing
transform applies its own, touching only the quote glyphs
and leaving every other strand and its anchors alone, each
straight mark sheared and its curled form woven in the same
place. Where the rule is wrong it is wrong in a knowable
way, and it is named rather than hidden: a leading
apostrophe, the one in tis or twas dropping the century, is
curled as an opening single quote when it should be a right
single quote standing in for the missing letters, because
the character before it is a space and the rule cannot tell
elision from quotation without a dictionary of contractions
it does not carry. That failure is measured in the tests and
left in this docstring rather than papered over, since a
smart-quote pass that claims to be always right is the kind
of tool that silently corrupts a linguistics paper full of
glottal-stop apostrophes. Only the two straight marks change;
dashes are deliberately left untouched.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.weave import Op

LEFT_DOUBLE = chr(0x201C)
RIGHT_DOUBLE = chr(0x201D)
LEFT_SINGLE = chr(0x2018)
RIGHT_SINGLE = chr(0x2019)


@dataclass
class QuoteResult:
    curled: int
    ops: list[Op]


def _opens(prev: str) -> bool:
    return prev == "" or prev.isspace() or prev in "([{"


def _target(glyph: str, prev: str) -> str:
    if glyph == '"':
        return LEFT_DOUBLE if _opens(prev) else RIGHT_DOUBLE
    if glyph == "'":
        return LEFT_SINGLE if _opens(prev) else RIGHT_SINGLE
    return glyph


def curl(author: Author, start: int, count: int) -> QuoteResult:
    weave = author.weave
    sources = [
        weave.strand_at_visible(start + offset).glyph
        for offset in range(count)
    ]
    lead = weave.strand_at_visible(start - 1).glyph if start > 0 else ""
    ids = [
        weave.strand_at_visible(start + offset).id
        for offset in range(count)
    ]
    minted: list[Op] = []
    curled = 0
    prev = lead
    for source, strand_id in zip(sources, ids, strict=True):
        target = _target(source, prev)
        prev = source
        if target == source:
            continue
        curled += 1
        position = weave.by_id[strand_id]
        visible = sum(
            1 for strand in weave.strands[:position] if not strand.sheared
        )
        minted.extend(author.erase_at(visible, 1))
        minted.extend(author.type_at(visible, target))
    return QuoteResult(curled=curled, ops=minted)
