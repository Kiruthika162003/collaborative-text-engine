"""Char frequency: the distribution of characters and its Shannon entropy.

Where the char-stats module counts characters by kind, this
counts them individually and measures how evenly they are
spread, which is what Shannon entropy captures: the bits per
character needed to name the next one given the distribution.
A text of one repeated character has entropy zero, because the
next character is never in doubt, and a text of two equally
frequent characters has entropy one, one bit to say which; the
more characters and the more evenly they occur, the higher the
entropy climbs. It is a measure of unpredictability over the
observed characters, not a compression ratio, and the
distinction is stated: real compressors exploit patterns
across characters that a per-character entropy cannot see, so
this number is a floor on the per-character cost, not a promise
of how small a file will get. The frequency map and the most-
common list are the raw distribution for a caller who wants the
shape rather than the summary, counted over exactly the
characters given including spaces and newlines, because those
are characters a text spends bits on too and excluding them
would measure a text the writer did not write. An empty text
has entropy zero, the honest floor, rather than an undefined
logarithm, since there is no next character to be uncertain
about.
"""

from __future__ import annotations

import math
from collections import Counter


def frequency(text: str) -> dict[str, int]:
    return dict(Counter(text))


def entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum(
        (count / total) * math.log2(count / total)
        for count in counts.values()
    )


def most_common(text: str, limit: int = 5) -> list[tuple[str, int]]:
    return Counter(text).most_common(limit)


def distinct(text: str) -> int:
    return len(set(text))
