"""Word index: an inverted index from words to the lines they appear on.

Searching a document for a word by scanning every line is fine
once and wasteful when a caller asks about many words, so this
builds the inverted index a search engine uses: a map from each
word to the lines it occurs on, built in one pass over the
text and then queried in constant time per word. The postings
for a word are the line numbers of its occurrences with
repeats, so the frequency of a word is the length of its
postings and the distinct lines it appears on are those
postings deduplicated, both available without rescanning. The
multi-word query is where an inverted index earns its name: the
lines that hold all of several words are the intersection of
their posting sets, computed from the index rather than by
re-reading the document, which is how a search for a phrase's
words narrows to candidate lines fast. Words are folded to
lowercase so a query matches regardless of the case in the
text, and the tokens are the letter runs the other modules
split on, so the index agrees with the rest of the engine
about what a word is. The index is built from a snapshot of the
text and does not update itself as the document changes, which
is stated: it is a query structure to build when needed and
rebuild after edits, not a live view, and treating a stale
index as current would return lines that have since moved,
the same staleness a stored position always risks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from loom.weave import Weave

WORD = re.compile(r"[A-Za-z']+")


@dataclass
class WordIndex:
    postings: dict[str, list[int]] = field(default_factory=dict)

    @classmethod
    def build(cls, weave: Weave) -> WordIndex:
        postings: dict[str, list[int]] = {}
        for line_number, line in enumerate(weave.text().split("\n")):
            for match in WORD.finditer(line):
                postings.setdefault(match.group(0).lower(), []).append(
                    line_number
                )
        return cls(postings=postings)

    def contains(self, word: str) -> bool:
        return word.lower() in self.postings

    def frequency(self, word: str) -> int:
        return len(self.postings.get(word.lower(), []))

    def lines_for(self, word: str) -> list[int]:
        return sorted(set(self.postings.get(word.lower(), [])))

    def lines_with_all(self, words: list[str]) -> list[int]:
        if not words:
            return []
        line_sets = [set(self.lines_for(word)) for word in words]
        common = set.intersection(*line_sets) if line_sets else set()
        return sorted(common)

    def vocabulary(self) -> list[str]:
        return sorted(self.postings)

    def __len__(self) -> int:
        return len(self.postings)
