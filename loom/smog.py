"""SMOG: a readability grade from the count of long words, extrapolated to a sample.

SMOG estimates the years of schooling a reader needs from one
signal, how many polysyllabic words a text uses, on the theory
that long words are what make prose hard. This counts the words
of three or more syllables, scales that count to the
thirty-sentence sample SMOG was calibrated on, and runs the
square-root formula. Two honesties come with it. First, the
syllable count is the readability module's heuristic, which
undercounts words like area and simile, so SMOG inherits those
misses; a text heavy in the words the heuristic trips on grades
slightly easy. Second, SMOG was built for samples of thirty
sentences and this extrapolates from whatever the document has
by the thirty-over-sentences factor, which is faithful to the
formula but means a three-sentence document's grade swings on
a single long word, so the score is meaningful for a passage
and noisy for a snippet, and that is named rather than
smoothed over. Like the other readability tools it grades
length, not thought, and having it beside Flesch and
Coleman-Liau lets a caller see three formulas built on three
different signals, syllables per word, letters per word, and
long words per sentence, agree or disagree, which says more
than any one alone. An empty document has no grade and returns
zero rather than a formula run on nothing.
"""

from __future__ import annotations

import math

from loom.prose import words_of
from loom.readability import sentence_count, syllables
from loom.weave import Weave


def polysyllables(weave: Weave) -> int:
    return sum(1 for word in words_of(weave) if syllables(word) >= 3)


def grade(weave: Weave) -> float:
    sentences = sentence_count(weave)
    if sentences == 0:
        return 0.0
    poly = polysyllables(weave)
    return round(1.043 * math.sqrt(poly * (30 / sentences)) + 3.1291, 1)


def report(weave: Weave) -> str:
    if sentence_count(weave) == 0:
        return "no sentences; SMOG needs prose to grade"
    return (
        f"SMOG grade {grade(weave)} from {polysyllables(weave)} long "
        "word(s); calibrated for thirty sentences, noisy on a snippet"
    )
