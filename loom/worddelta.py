"""Word delta: which words a revision added and removed, counted as a multiset.

The word-diff module compares two texts as sequences, caring
where each word sits; this compares them as bags of words,
caring only how many of each there are, which answers a
different question, what vocabulary changed between two
drafts. It counts the words of each text, folding case so The
and the are the same word, and reports the multiset
difference: the words the after has that the before did not,
and the words the before had that the after dropped, each with
how many copies changed. Because it is a multiset difference,
a word merely moved to a new position counts as neither added
nor removed, since the bag still holds it, which is exactly
right for the question of what vocabulary changed and exactly
wrong for the question of what moved, so a caller who cares
about order wants the sequence diff instead and this says so.
Repeated words are handled by count, so a draft that went from
one the to three thes reports two thes added rather than a
boolean that hides the repetition. It is pure over the two
strings, position ignored, which is the property that makes it
cheap and the reason it cannot tell a rewrite that kept every
word from no change at all: same words, same counts, empty
delta, whatever the sentences now say.
"""

from __future__ import annotations

from collections import Counter


def _bag(text: str) -> Counter:
    return Counter(text.lower().split())


def added(before: str, after: str) -> dict[str, int]:
    return dict(_bag(after) - _bag(before))


def removed(before: str, after: str) -> dict[str, int]:
    return dict(_bag(before) - _bag(after))


def net_words(before: str, after: str) -> int:
    return len(after.split()) - len(before.split())


def changed(before: str, after: str) -> bool:
    return _bag(before) != _bag(after)
