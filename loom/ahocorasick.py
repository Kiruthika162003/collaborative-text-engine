"""Aho-Corasick: match a whole dictionary of patterns against the text in a single pass.

Searching a text for one pattern is what the prefix-table and
rolling-hash searches do; searching it for many at once, a
dictionary of words to flag, a set of forbidden phrases, is what
Aho-Corasick does without running a separate search per pattern.
It weaves all the patterns into one automaton. The patterns first
become a trie, a tree where a path from the root spells a pattern's
prefix and a node marks where a whole pattern ends, so shared
prefixes share a path. Then each node gets a failure link, the
generalization of the prefix table's border: it points to the node
spelling the longest proper suffix of the current path that is also
some pattern's prefix, so that when the text mismatches at a node
the automaton falls back along the link to the longest other
pattern still alive rather than starting over. Following the text
character by character, the automaton advances on a match and
follows failure links on a mismatch, never moving the text cursor
back, and at each node it reports every pattern that ends there,
including the shorter patterns that end there by way of the failure
links, which is why an output at one node can carry several
matches. I had guessed searching for many patterns just meant
looping a single-pattern search once per pattern, paying the text
length times the number of patterns; it does not, the automaton
reads the text once no matter how many patterns it holds, and the
whole cost is the text length plus the total length of the
patterns to build the automaton plus the number of matches
reported, with the count of patterns appearing nowhere in that as
a multiplier. That independence from the number of patterns is the
point, and it is why a content filter or a tokenizer with a large
vocabulary reaches for this rather than a loop of searches. The
failure links are computed breadth-first so that a node's link is
always into a shallower node already finished, and each node
inherits its failure node's outputs when it is built, so the search
itself only has to read the outputs already gathered at the node it
lands on.
"""

from __future__ import annotations

from collections import deque


class _State:
    __slots__ = ("children", "fail", "outputs")

    def __init__(self) -> None:
        self.children: dict = {}
        self.fail: _State | None = None
        self.outputs: list = []


class AhoCorasick:
    __slots__ = ("_patterns", "_root")

    def __init__(self, patterns: list) -> None:
        self._root = _State()
        self._patterns = [pattern for pattern in patterns if pattern]
        for pattern in self._patterns:
            self._add(pattern)
        self._build()

    def _add(self, pattern: str) -> None:
        node = self._root
        for symbol in pattern:
            node = node.children.setdefault(symbol, _State())
        node.outputs.append(pattern)

    def _build(self) -> None:
        queue: deque = deque()
        for child in self._root.children.values():
            child.fail = self._root
            queue.append(child)
        while queue:
            node = queue.popleft()
            for symbol, child in node.children.items():
                fail = node.fail
                while fail is not None and symbol not in fail.children:
                    fail = fail.fail
                child.fail = fail.children[symbol] if fail is not None else self._root
                if child.fail is child:
                    child.fail = self._root
                child.outputs = child.outputs + child.fail.outputs
                queue.append(child)

    def search(self, text: str) -> list:
        found = []
        node = self._root
        for index, symbol in enumerate(text):
            while node is not self._root and symbol not in node.children:
                node = node.fail
            node = node.children.get(symbol, self._root)
            for pattern in node.outputs:
                found.append((index - len(pattern) + 1, pattern))
        return sorted(found)

    def contains_any(self, text: str) -> bool:
        node = self._root
        for symbol in text:
            while node is not self._root and symbol not in node.children:
                node = node.fail
            node = node.children.get(symbol, self._root)
            if node.outputs:
                return True
        return False

    def count(self, text: str) -> int:
        return len(self.search(text))
