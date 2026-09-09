"""Did you mean: the closest words to a misspelling, by edit distance over a vocabulary.

Where spellwatch asks whether a word is in a lexicon and
completion finishes a prefix, this answers the other question,
what did the writer probably mean, by finding the vocabulary
words closest to the one they typed. Closeness is the edit
distance the edit-cost module computes, the fewest single-
character changes between two words, and the suggestions are
the candidates within a small distance, ranked nearest first
and alphabetically among ties so the same misspelling always
suggests the same list. The vocabulary can be a caller's word
set or the document's own words, which is the useful default
in a shared document, because the word a writer fumbled is
usually one already in the text and suggesting from the
document keeps the terminology consistent. The honest limit is
the distance metric's: it is Levenshtein, so a transposition
like recieve for receive costs two, the same as two unrelated
substitutions, which means a transposed spelling can rank a
genuinely different word above its intended correction; that
is the classic tradeoff a Damerau distance would fix and this
does not, named rather than hidden so a caller reads a
surprising suggestion as the metric working as described. The
maximum distance is small by default, because a suggestion
five edits away is not a correction but a different word, and
offering it would be noise dressed as help.
"""

from __future__ import annotations

import re

from loom.editcost import distance
from loom.weave import Weave

WORD = re.compile(r"[A-Za-z']+")


def nearest(
    word: str,
    candidates: set[str],
    limit: int = 3,
    max_distance: int = 2,
) -> list[tuple[str, int]]:
    scored = [
        (candidate, distance(word, candidate))
        for candidate in candidates
        if candidate != word
    ]
    within = [(c, d) for c, d in scored if d <= max_distance]
    return sorted(within, key=lambda pair: (pair[1], pair[0]))[:limit]


def did_you_mean(word: str, candidates: set[str]) -> str | None:
    hits = nearest(word, candidates, limit=1)
    return hits[0][0] if hits else None


def _vocabulary(weave: Weave) -> set[str]:
    return {match.group(0).lower() for match in WORD.finditer(weave.text())}


def suggest(weave: Weave, word: str, limit: int = 3) -> list[tuple[str, int]]:
    return nearest(word.lower(), _vocabulary(weave), limit)
