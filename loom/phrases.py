"""Phrases: repeated word sequences, the phrase-level companion to single-word keywords.

Keywords count single words; this counts sequences, the two-
and three-word runs a document repeats, which catch what a
single-word count cannot: a phrase a writer leans on, a term
of art that is two words, a stock transition that recurs. It
builds the n-grams, every run of n consecutive words, counts
them, and reports the ones that repeat, which is where the
signal is, since a phrase said once is just prose and a phrase
said five times is a habit or a keyword. Words are lowercased
so The Cat and the cat count as one phrase, and the honest
omission is stated: it does not filter stopwords, so in
ordinary text the top phrases are of the and in the and their
kind, the function-word runs that dominate any n-gram count,
and a caller wanting topical phrases should lean on the
keywords module for the words and read this for the shape.
That is a deliberate division of labour rather than a gap:
folding a stoplist in here would bake one module's judgement
into another's counts, and keeping phrases a pure frequency
lets a caller combine it with whatever filtering they choose.
The n is the caller's, two by default for the common case, and
a request for zero-length or negative phrases is refused
rather than returning the empty runs that would follow.
"""

from __future__ import annotations

import re

from loom.errors import Invalid

WORD = re.compile(r"[A-Za-z']+")


def _words(text: str) -> list[str]:
    return [match.group(0).lower() for match in WORD.finditer(text)]


def ngrams(text: str, n: int = 2) -> list[tuple[str, ...]]:
    if n < 1:
        raise Invalid("a phrase has at least one word")
    words = _words(text)
    return [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]


def frequencies(text: str, n: int = 2) -> dict[str, int]:
    counts: dict[str, int] = {}
    for gram in ngrams(text, n):
        phrase = " ".join(gram)
        counts[phrase] = counts.get(phrase, 0) + 1
    return counts


def repeated(
    text: str, n: int = 2, min_count: int = 2
) -> list[tuple[str, int]]:
    counts = frequencies(text, n)
    hits = [
        (phrase, count)
        for phrase, count in counts.items()
        if count >= min_count
    ]
    return sorted(hits, key=lambda pair: (-pair[1], pair[0]))


def report(text: str, n: int = 2) -> str:
    hits = repeated(text, n)
    if not hits:
        return f"no {n}-word phrase repeats"
    body = ", ".join(f"{phrase!r} ({count})" for phrase, count in hits)
    return f"repeated {n}-word phrase(s): {body}"
