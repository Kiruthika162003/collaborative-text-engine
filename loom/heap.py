"""Heap: a binary min-heap, the priority queue that always yields the smallest.

A min-heap keeps a collection so that the smallest item is
always at hand, which is what a priority queue needs and what a
plain list does slowly. It stores the items in an array as an
implicit binary tree, each item's children at twice-its-index-
plus-one and plus-two, and maintains the heap property that a
parent is never larger than its children. Pushing appends the
item and sifts it up, swapping it toward the root while it is
smaller than its parent, so it settles at the right level;
popping takes the root, the smallest, moves the last item to
the root, and sifts it down, swapping it toward the leaves past
its smaller child until it settles. Both operations touch only
a path from root to leaf, the height of the tree, which is
logarithmic in the count, so a heap pushes and pops many items
far faster than sorting the whole collection after each change.
Popping an empty heap is refused rather than returning a
sentinel, because there is no smallest of nothing and a
sentinel would be mistaken for a real value; a caller checks
the length or catches the refusal. The items must be
comparable to each other, since the heap orders by comparison,
and a caller wanting a max-heap or a keyed priority pushes
negated values or key-tagged tuples, the standard tricks,
rather than this carrying a comparator, which keeps the
structure simple and its ordering the plain one the items
already have.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid


@dataclass
class MinHeap:
    items: list = field(default_factory=list)

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self.items[index] < self.items[parent]:
                self.items[index], self.items[parent] = (
                    self.items[parent],
                    self.items[index],
                )
                index = parent
            else:
                break

    def _sift_down(self, index: int) -> None:
        count = len(self.items)
        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2
            if left < count and self.items[left] < self.items[smallest]:
                smallest = left
            if right < count and self.items[right] < self.items[smallest]:
                smallest = right
            if smallest == index:
                break
            self.items[index], self.items[smallest] = (
                self.items[smallest],
                self.items[index],
            )
            index = smallest

    def push(self, item) -> None:
        self.items.append(item)
        self._sift_up(len(self.items) - 1)

    def pop(self):
        if not self.items:
            raise Invalid("pop from an empty heap")
        top = self.items[0]
        last = self.items.pop()
        if self.items:
            self.items[0] = last
            self._sift_down(0)
        return top

    def peek(self):
        if not self.items:
            raise Invalid("peek at an empty heap")
        return self.items[0]

    def __len__(self) -> int:
        return len(self.items)


def heapsort(values: list) -> list:
    heap = MinHeap()
    for value in values:
        heap.push(value)
    return [heap.pop() for _ in range(len(heap))]
