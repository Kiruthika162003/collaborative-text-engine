"""Casing: change the case of a range while touching only the glyphs that change.

Upppercasing a selection feels like a formatting toggle, but
in a sequence CRDT a glyph's case is not an attribute you
flip; the glyph itself is replaced, a lowercase a sheared
and an uppercase A woven in its place, because the two are
different characters and the weave stores characters. So a
case transform is a run of shears and inserts, and the one
discipline that earns its keep is touching only the glyphs
whose case actually differs: an uppercase word inside a
range being uppercased is left exactly as it stands, its
strands and any anchor riding them untouched, where a
transform that rewrote every glyph would orphan a comment
pinned to a letter that never needed changing. The strand
ids for the range are resolved before any operation is
minted, the same guard replace keeps, and each surviving
glyph's live position is recomputed from its id as it is
reached, so an insert that lengthens the text, a sharp s
becoming two letters when uppercased, does not corrupt the
positions of the glyphs still waiting. Title case takes the
glyph before the range as its context so a range beginning
mid-word is not falsely capitalised, and sentence case
carries the same context so a selection starting after a
period opens with a capital and one starting mid-sentence
does not. A transform that changes nothing mints nothing
and reports zero changed rather than a success it did not
earn.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.weave import Op

TERMINALS = ".!?"


@dataclass
class CaseResult:
    changed: int
    ops: list[Op]


def _targets(text: str, mode: str, lead: str, opening: bool) -> list[str]:
    if mode == "upper":
        return [glyph.upper() for glyph in text]
    if mode == "lower":
        return [glyph.lower() for glyph in text]
    if mode == "title":
        result = []
        prev = lead
        for glyph in text:
            boundary = not prev.isalnum()
            if boundary and glyph.isalpha():
                result.append(glyph.upper())
            else:
                result.append(glyph.lower())
            prev = glyph
        return result
    if mode == "sentence":
        result = []
        at_start = opening
        for glyph in text:
            if glyph.isalpha():
                result.append(glyph.upper() if at_start else glyph.lower())
                at_start = False
            else:
                result.append(glyph)
                if glyph in TERMINALS:
                    at_start = True
        return result
    raise ValueError(f"unknown case mode {mode!r}")


def _opening(author: Author, start: int) -> bool:
    index = start - 1
    while index >= 0:
        glyph = author.weave.strand_at_visible(index).glyph
        if glyph.isspace():
            index -= 1
            continue
        return glyph in TERMINALS
    return True


def _transform(
    author: Author, start: int, count: int, mode: str
) -> CaseResult:
    weave = author.weave
    sources = [
        weave.strand_at_visible(start + offset).glyph
        for offset in range(count)
    ]
    lead = weave.strand_at_visible(start - 1).glyph if start > 0 else ""
    targets = _targets(
        "".join(sources), mode, lead, _opening(author, start)
    )
    ids = [weave.strand_at_visible(start + offset).id for offset in range(count)]
    minted: list[Op] = []
    changed = 0
    for source, target, strand_id in zip(sources, targets, ids, strict=True):
        if target == source:
            continue
        changed += 1
        position = weave.by_id[strand_id]
        visible = sum(
            1 for strand in weave.strands[:position] if not strand.sheared
        )
        minted.extend(author.erase_at(visible, 1))
        if target:
            minted.extend(author.type_at(visible, target))
    return CaseResult(changed=changed, ops=minted)


def upper(author: Author, start: int, count: int) -> CaseResult:
    return _transform(author, start, count, "upper")


def lower(author: Author, start: int, count: int) -> CaseResult:
    return _transform(author, start, count, "lower")


def title(author: Author, start: int, count: int) -> CaseResult:
    return _transform(author, start, count, "title")


def sentence(author: Author, start: int, count: int) -> CaseResult:
    return _transform(author, start, count, "sentence")
