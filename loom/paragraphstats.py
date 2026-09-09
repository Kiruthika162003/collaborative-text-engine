"""Paragraph stats: the shape of each paragraph, so a writer can find the long one.

A document's readability lives paragraph by paragraph, and a
writer editing for clarity wants to find the one paragraph
that ran to three hundred words or the sentence that never
stopped, not a single number for the whole draft. This
measures each paragraph on its own: how many words it holds,
how many sentences, and how long its longest sentence ran,
the three numbers that between them catch the wall of text
and the runaway sentence. The paragraph and sentence
boundaries are the same ones the paragraphs and sentences
modules read by, blank lines splitting paragraphs and
terminal punctuation splitting sentences, so the stats agree
with the rest of the outline tools rather than inventing a
private notion of where a paragraph ends. The thresholds
that flag a paragraph long or a sentence overlong are
conventions, not laws, and they are named and adjustable,
because a hundred and twenty words is a lot for a memo and
nothing for an essay, and a tool that hid its threshold
would be passing an opinion off as a measurement. What the
module reports is the measurement; whether a long paragraph
is a problem is the writer's call, the same restraint every
reading organ here keeps, since a paragraph is sometimes long
because the thought is, and no word count knows the
difference.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.paragraphs import blocks
from loom.weave import Weave

TERMINAL = re.compile(r"[.!?]+")
LONG_PARAGRAPH = 120
LONG_SENTENCE = 35


@dataclass(frozen=True)
class ParaStat:
    ordinal: int
    words: int
    sentences: int
    longest_sentence: int


def _sentences(text: str) -> list[str]:
    parts = [part for part in TERMINAL.split(text) if part.strip()]
    return parts or [text]


def para_stats(weave: Weave) -> list[ParaStat]:
    result = []
    for block in blocks(weave):
        sentences = _sentences(block.text)
        longest = max((len(part.split()) for part in sentences), default=0)
        result.append(
            ParaStat(
                ordinal=block.ordinal,
                words=len(block.text.split()),
                sentences=len(sentences),
                longest_sentence=longest,
            )
        )
    return result


def long_paragraphs(
    weave: Weave, threshold: int = LONG_PARAGRAPH
) -> list[int]:
    return [
        stat.ordinal
        for stat in para_stats(weave)
        if stat.words > threshold
    ]


def runaway_sentences(
    weave: Weave, threshold: int = LONG_SENTENCE
) -> list[int]:
    return [
        stat.ordinal
        for stat in para_stats(weave)
        if stat.longest_sentence > threshold
    ]


def report(weave: Weave) -> str:
    stats = para_stats(weave)
    if not stats:
        return "no paragraphs to measure"
    lines = [f"{len(stats)} paragraph(s):"]
    for stat in stats:
        lines.append(
            f"  {stat.ordinal}: {stat.words} word(s), "
            f"{stat.sentences} sentence(s), longest "
            f"{stat.longest_sentence} word(s)"
        )
    lines.append(
        "measurements, not verdicts; a paragraph is sometimes "
        "long because the thought is"
    )
    return "\n".join(lines)
