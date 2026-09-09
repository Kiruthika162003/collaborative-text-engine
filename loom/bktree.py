"""BK-tree: a metric tree for fuzzy word search that prunes by the triangle inequality.

The did-you-mean module finds near words by measuring the
distance to every candidate, which is fine for a small
vocabulary and slow for a large one. A BK-tree does the same
search without measuring most candidates, by exploiting that
edit distance is a metric and so obeys the triangle
inequality: a word within distance k of the query can only sit
on a branch whose edge distance from the current node is within
k of the query's distance to that node, so every other branch
is skipped without a single comparison inside it. The tree is
built by hanging each new word off an existing node under the
edge equal to their distance, and a word already present is not
added twice. The search walks from the root, keeps any node
within the tolerance, and follows only the branches the
triangle bound cannot rule out, which turns a scan of the whole
vocabulary into a walk down a few branches. The results come
back nearest first, ties alphabetical, the same order the
linear scanner returns so the two are interchangeable at the
interface and differ only in speed. It inherits the edit-cost
module's distance, so it shares that metric's properties,
including that a transposition costs two, and it is a build-
once structure like the word index: built from a vocabulary
and queried many times, rebuilt when the vocabulary changes,
because the tree's shape depends on the words in it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.editcost import distance


@dataclass
class _Node:
    word: str
    children: dict[int, _Node] = field(default_factory=dict)


@dataclass
class BKTree:
    root: _Node | None = None
    size: int = 0

    def add(self, word: str) -> None:
        if self.root is None:
            self.root = _Node(word)
            self.size = 1
            return
        node = self.root
        while True:
            gap = distance(word, node.word)
            if gap == 0:
                return
            child = node.children.get(gap)
            if child is None:
                node.children[gap] = _Node(word)
                self.size += 1
                return
            node = child

    def find(self, word: str, max_distance: int) -> list[tuple[str, int]]:
        matches: list[tuple[str, int]] = []
        if self.root is None:
            return matches
        stack = [self.root]
        while stack:
            node = stack.pop()
            gap = distance(word, node.word)
            if gap <= max_distance:
                matches.append((node.word, gap))
            low = gap - max_distance
            high = gap + max_distance
            for edge, child in node.children.items():
                if low <= edge <= high:
                    stack.append(child)
        return sorted(matches, key=lambda match: (match[1], match[0]))

    def __len__(self) -> int:
        return self.size


def of_words(words: list[str]) -> BKTree:
    tree = BKTree()
    for word in words:
        tree.add(word)
    return tree
