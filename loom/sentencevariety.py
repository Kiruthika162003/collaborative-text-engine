"""Sentence variety: the spread of sentence lengths, a descriptive measure of rhythm.

Prose reads monotonous when every sentence runs the same
length and lively when they vary, and this measures that
spread: the length in words of each sentence, their mean, and
the standard deviation that says how much they stray from it.
A deviation near zero is a document of same-length sentences,
a metronome; a larger one is a document that mixes short and
long, the rhythm most writing guides recommend. The lengths
come from the sentences module, so the boundaries are the ones
the rest of the outline tools read by, and the statistics are
the plain population formulas, mean and the deviation about
it, computed over the sentences present. It is descriptive and
says so in the reading-organ tradition: low variety is a flaw
in an essay and a virtue in a list of terse instructions, and
no deviation knows which it is reading, so the number is the
measurement and the judgement is the writer's. An empty
document has no sentences and reports zero for every figure
without pretending a spread it has no data for, and a single
sentence has a mean equal to its length and a deviation of
zero, which is the truth: one sentence cannot vary from
itself, and a variety score that implied otherwise would be
inventing spread from a sample of one.
"""

from __future__ import annotations

import math

from loom.sentences import sentences
from loom.weave import Weave


def sentence_lengths(weave: Weave) -> list[int]:
    return [len(sentence.text.split()) for sentence in sentences(weave)]


def mean_length(weave: Weave) -> float:
    lengths = sentence_lengths(weave)
    return sum(lengths) / len(lengths) if lengths else 0.0


def variance(weave: Weave) -> float:
    lengths = sentence_lengths(weave)
    if not lengths:
        return 0.0
    mean = sum(lengths) / len(lengths)
    return sum((length - mean) ** 2 for length in lengths) / len(lengths)


def stddev_length(weave: Weave) -> float:
    return math.sqrt(variance(weave))


def report(weave: Weave) -> str:
    lengths = sentence_lengths(weave)
    if not lengths:
        return "no sentences; no rhythm to measure"
    return (
        f"{len(lengths)} sentence(s), mean {mean_length(weave):.1f} "
        f"word(s), deviation {stddev_length(weave):.1f}; "
        "variety is descriptive, not a verdict"
    )
