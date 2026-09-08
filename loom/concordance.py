"""Concordance: which words appear, how often, and where, for the whole cloth.

A concordance is the oldest reading tool there is, and for
a living document it answers the questions a writer asks
about their own prose: which word have I leaned on, how
many distinct words did I actually use, and where does this
term appear so I can check I used it consistently. Words
are lowercased runs of letters and digits, punctuation
stripped so quick and quick, are one word, because a
concordance that counts them separately is measuring
typography rather than vocabulary. The positions recorded
are visible offsets computed at query time, honest about
being weather, so a writer can jump to each occurrence in
the document as it currently reads. The vocabulary richness
is distinct words over total words, a number that rises
with variety and falls with repetition, reported as a
ratio and never as a grade, because the loom measures the
prose and lets the writer judge it. Stop words are not
filtered, because whose stop list, and a concordance that
silently hides the and is a concordance arguing about
style while pretending to count.
"""

from __future__ import annotations

import re
from collections import Counter

from loom.weave import Weave

WORD = re.compile(r"[a-z0-9]+")


def _words(weave: Weave) -> list[str]:
    return WORD.findall(weave.text().lower())


def frequencies(weave: Weave) -> Counter:
    return Counter(_words(weave))


def distinct(weave: Weave) -> int:
    return len(frequencies(weave))


def richness(weave: Weave) -> float:
    words = _words(weave)
    if not words:
        return 0.0
    return round(len(set(words)) / len(words), 3)


def positions(weave: Weave, word: str) -> list[int]:
    target = word.lower()
    found = []
    for match in WORD.finditer(weave.text().lower()):
        if match.group() == target:
            found.append(match.start())
    return found


def top(
    weave: Weave, count: int = 5
) -> list[tuple[str, int]]:
    return frequencies(weave).most_common(count)


def report(weave: Weave) -> str:
    words = _words(weave)
    if not words:
        return "an empty page has no vocabulary"
    lines = [
        f"{len(words)} word(s), {distinct(weave)} "
        f"distinct, richness {richness(weave)}:"
    ]
    for word, hits in top(weave, 5):
        lines.append(f"  {word}: {hits}")
    lines.append(
        "no stop words filtered; whose stop list, and "
        "a concordance that hides 'the' is arguing "
        "about style while pretending to count"
    )
    return "\n".join(lines)
