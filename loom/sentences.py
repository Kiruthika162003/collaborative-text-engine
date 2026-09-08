"""Sentences: the cloth split at full stops, each sentence pinned to its first strand.

Where paragraphs split on blank lines, sentences split on
terminal punctuation, a run of full stops, exclamation
marks, or question marks followed by whitespace or the end
of the text, which is how a reader parses one and how a
select-sentence gesture needs it parsed. Each sentence pins
to its first non-space strand so a bookmark on the third
sentence survives edits above it, the same pin discipline
paragraphs and headings keep, and the sentence a position
sits in is found by walking to the pins rather than stored,
because a sentence boundary moves the instant someone types
a period. The heuristic is honest about its one famous
failure: it splits Mr. Smith into two sentences, reading the
period after Mr as a full stop, because telling an
abbreviation's dot from a sentence's dot needs a list of
abbreviations this module does not carry, and that
over-split is measured in the tests and named here rather
than hidden behind a boundary count that looks authoritative.
Newlines inside a sentence are whitespace, not breaks, so a
sentence wrapped across two lines is still one sentence,
which is what the writer meant even if the editor wrapped
it for them.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Missing
from loom.ids import OpId
from loom.weave import Weave

TERMINAL = ".!?"


@dataclass(frozen=True)
class Sentence:
    pin: OpId
    text: str
    ordinal: int


def _visible(weave: Weave) -> list[tuple[OpId, str]]:
    return [
        (strand.id, strand.glyph)
        for strand in weave.strands
        if not strand.sheared
    ]


def sentences(weave: Weave) -> list[Sentence]:
    seq = _visible(weave)
    found: list[Sentence] = []
    glyphs: list[str] = []
    pin: OpId | None = None
    ordinal = 0
    index = 0
    total = len(seq)
    while index < total:
        strand_id, glyph = seq[index]
        if pin is None and not glyph.isspace():
            pin = strand_id
        if pin is not None:
            glyphs.append(glyph)
        if glyph in TERMINAL:
            index += 1
            while index < total and seq[index][1] in TERMINAL:
                glyphs.append(seq[index][1])
                index += 1
            if index >= total or seq[index][1].isspace():
                text = "".join(glyphs).strip()
                if pin is not None and text:
                    found.append(
                        Sentence(pin=pin, text=text, ordinal=ordinal)
                    )
                    ordinal += 1
                glyphs = []
                pin = None
            continue
        index += 1
    text = "".join(glyphs).strip()
    if pin is not None and text:
        found.append(Sentence(pin=pin, text=text, ordinal=ordinal))
    return found


def sentence_count(weave: Weave) -> int:
    return len(sentences(weave))


def sentence_of(weave: Weave, strand_id: OpId) -> int:
    target = weave.by_id.get(strand_id)
    if target is None:
        raise Missing(f"{strand_id.wire()} is not in the fabric")
    candidate = 0
    for sentence in sentences(weave):
        if weave.by_id[sentence.pin] <= target:
            candidate = sentence.ordinal
        else:
            break
    return candidate


def render(weave: Weave) -> str:
    held = sentences(weave)
    if not held:
        return "no sentences; the cloth has no full stops"
    lines = [f"{len(held)} sentence(s):"]
    for sentence in held:
        head = sentence.text[:40]
        if len(sentence.text) > 40:
            head += "..."
        lines.append(f"  {sentence.ordinal}: {head!r}")
    return "\n".join(lines)
