"""Readability: Flesch's arithmetic, reported as arithmetic and nothing more.

The prose module refuses a readability score on principle,
calling a number that grades prose an opinion wearing a lab
coat, and this module does not disagree with a word of it.
What it computes is not a judgment of thought but a
mechanical function of two lengths, how many words fall
between full stops and how many syllables fall inside a
word, which is all Flesch ever measured. An editor
comparing two drafts of the same paragraph sometimes wants
those two lengths reduced to one comparable figure, and the
formula does that and only that; it cannot tell a clear
short sentence from a vapid one, and this module says so out
loud rather than letting the number imply otherwise. The
honest trouble lives in the syllable count, which no
heuristic gets fully right without a dictionary: the
vowel-group rule counts area as two syllables when it has
three and simile as two when it has three, both measured
and recorded here rather than guessed at, because a
readability figure built on a syllable count that lies
about its own accuracy is two errors stacked and sold as
one. Queue, the word that looks like it should defeat the
rule, the rule actually gets right, one syllable, which is
worth keeping beside the failures so the heuristic is
neither trusted blindly nor dismissed whole.
"""

from __future__ import annotations

import re

from loom.weave import Weave

VOWELS = "aeiouy"
TERMINAL = re.compile(r"[.!?]+")


def syllables(word: str) -> int:
    core = "".join(glyph for glyph in word.lower() if glyph.isalpha())
    if not core:
        return 0
    count = 0
    prev_vowel = False
    for glyph in core:
        is_vowel = glyph in VOWELS
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if core.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def sentence_count(weave: Weave) -> int:
    text = weave.text().strip()
    if not text:
        return 0
    parts = [part for part in TERMINAL.split(text) if part.strip()]
    return max(len(parts), 1)


def syllable_total(weave: Weave) -> int:
    return sum(syllables(word) for word in weave.text().split())


def _lengths(weave: Weave) -> tuple[int, int, int]:
    words = weave.text().split()
    return len(words), sentence_count(weave), syllable_total(weave)


def flesch_reading_ease(weave: Weave) -> float:
    words, sentences, syllable_sum = _lengths(weave)
    if words == 0 or sentences == 0:
        return 0.0
    score = (
        206.835
        - 1.015 * (words / sentences)
        - 84.6 * (syllable_sum / words)
    )
    return round(score, 1)


def flesch_kincaid_grade(weave: Weave) -> float:
    words, sentences, syllable_sum = _lengths(weave)
    if words == 0 or sentences == 0:
        return 0.0
    grade = (
        0.39 * (words / sentences)
        + 11.8 * (syllable_sum / words)
        - 15.59
    )
    return round(grade, 1)


def report(weave: Weave) -> str:
    words, sentences, syllable_sum = _lengths(weave)
    if words == 0:
        return "no prose to measure; readability needs words to count"
    return "\n".join(
        [
            f"{words} word(s), {sentences} sentence(s), "
            f"{syllable_sum} syllable(s) by the vowel-group rule",
            f"reading ease {flesch_reading_ease(weave)}, "
            f"grade {flesch_kincaid_grade(weave)}",
            "these grade sentence and word length, not thought; "
            "the prose module was right about that",
        ]
    )
