"""Trie: a prefix tree for words, answering prefix questions the fast way.

A trie stores words as paths down a tree of single-character
edges, which is the right shape for the questions a completer
and a dictionary ask: does this word exist, is any word
prefixed by this, and what are all the words under this
prefix. Each is a walk down the tree rather than a scan over a
list, so a large vocabulary answers a prefix query in the
length of the prefix, not the size of the vocabulary, which is
why an editor's autocomplete reaches for a trie rather than
filtering a word list on every keystroke. The end of a word is
marked with a sentinel that is not a character, so a word can
end anywhere along a path that continues to longer words, cat
ending where cats keeps going, and no real character can
collide with the marker. Inserting the same word twice does
not inflate the count, because a set of words holds each once
and the count is the size of that set, not the number of
insertions. Words under a prefix come back in sorted order, a
depth-first walk taking the children alphabetically, so the
same trie always lists a prefix's words the same way, which a
completer needs to rank them predictably. The trie stores
whatever strings it is given and reads them back exactly; it
does not fold case or normalize, because a caller who wants
case-insensitive lookup lowercases on the way in and out, and
baking that choice into the structure would take it away from
a caller who needs the case kept.
"""

from __future__ import annotations

from dataclasses import dataclass, field

END = None


@dataclass
class Trie:
    root: dict = field(default_factory=dict)
    size: int = 0

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.setdefault(char, {})
        if END not in node:
            self.size += 1
        node[END] = True

    def _walk(self, text: str) -> dict | None:
        node = self.root
        for char in text:
            if char not in node:
                return None
            node = node[char]
        return node

    def contains(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and END in node

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def words_with_prefix(self, prefix: str) -> list[str]:
        node = self._walk(prefix)
        if node is None:
            return []
        found: list[str] = []

        def walk(current: dict, suffix: str) -> None:
            if END in current:
                found.append(prefix + suffix)
            for char in sorted(key for key in current if key is not END):
                walk(current[char], suffix + char)

        walk(node, "")
        return found

    def __len__(self) -> int:
        return self.size
