"""Diversity: lexical variety measured as the type-token ratio, with its length flaw fixed.

Lexical diversity is how much a text repeats itself, and the
classic measure is the type-token ratio, the count of distinct
words over the count of all words: a text that says ten
different words once scores one, a text that says one word ten
times scores a tenth. This computes it, folding case so The
and the are one type, and it is upfront about the metric's
famous flaw: the raw ratio falls as a text grows, because a
longer text reuses common words no matter how varied its
vocabulary, so two texts of different lengths cannot be
compared by their raw ratios at all. The fix is the windowed
ratio, which measures the type-token ratio over fixed-size
windows and averages them, so every text is scored on the
same denominator and length stops distorting the number; this
provides both, the raw ratio for a caller who knows their
texts are the same length and the windowed one for the honest
cross-length comparison. Neither is a quality score, and the
module says so in the tradition of every reading organ here:
a low diversity is right for a technical document that must
repeat its terms and wrong for prose that should not, and no
ratio knows which it is reading. It reports the measurement
and leaves the meaning to the reader who knows the genre.
"""

from __future__ import annotations

from loom.prose import words_of
from loom.weave import Weave

DEFAULT_WINDOW = 100


def _words(weave: Weave) -> list[str]:
    return [word.lower() for word in words_of(weave)]


def type_token_ratio(weave: Weave) -> float:
    words = _words(weave)
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def windowed_ttr(weave: Weave, window: int = DEFAULT_WINDOW) -> float:
    words = _words(weave)
    if len(words) < window:
        return type_token_ratio(weave)
    ratios = [
        len(set(words[start : start + window])) / window
        for start in range(0, len(words) - window + 1, window)
    ]
    return sum(ratios) / len(ratios)


def report(weave: Weave) -> str:
    words = _words(weave)
    if not words:
        return "no words; nothing to measure for diversity"
    return (
        f"type-token ratio {type_token_ratio(weave):.2f} over "
        f"{len(words)} word(s); raw ratio falls with length, "
        "not a quality score"
    )
