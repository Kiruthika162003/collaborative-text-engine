"""Fenwick tree: prefix sums and point updates in one array, addressed by the lowest set bit.

Keeping a running total that supports both changing a single
element and asking for the sum of a prefix pulls in two
directions: a plain array of the values answers a point update at
once but sums a prefix by scanning it, while an array of prefix
sums answers the sum at once but rewrites half of itself on a
single update. The Fenwick tree threads between them by storing
neither the values nor the prefix sums but a set of partial sums
chosen so that both operations touch only a few entries. Each slot
owns a range of the data, and the length of that range is the
value of the lowest set bit of the slot's index, so slot eight
covers eight elements, slot twelve covers four, slot six covers
two, and an odd slot covers just itself. To sum a prefix you start
at its length and repeatedly strip off the lowest set bit, adding
the slot you land on, which walks a prefix down to zero in as many
steps as the index has one-bits; to update an element you start at
its slot and repeatedly add the lowest set bit, climbing through
exactly the slots whose ranges cover it. Both are the number of
one-bits in an index, which is at most the logarithm of the size,
so each is logarithmic and neither scans. I had guessed the
structure needed a node per element the way a segment tree does,
picturing a tree of objects; it needs exactly one array the length
of the data and no nodes at all, because the tree is implicit in
the arithmetic of the lowest set bit, which is the whole elegance
of it and the reason it is so much smaller than the segment tree
that answers the same prefix-sum question. The cost of that
smallness is reach: this answers prefix sums and, by subtracting
two of them, range sums, but it does not carry the range minimum
or maximum a segment tree can, because those do not subtract, and
that is the honest boundary of what the lowest-set-bit trick
buys.
"""

from __future__ import annotations

from loom.errors import Invalid


class Fenwick:
    __slots__ = ("_size", "_tree")

    def __init__(self, size: int) -> None:
        if size < 0:
            raise Invalid("a Fenwick tree cannot have negative length")
        self._size = size
        self._tree = [0] * (size + 1)

    @classmethod
    def from_values(cls, values: list) -> Fenwick:
        tree = cls(len(values))
        for index, value in enumerate(values):
            tree.add(index, value)
        return tree

    def __len__(self) -> int:
        return self._size

    def _check(self, index: int) -> None:
        if not 0 <= index < self._size:
            raise Invalid(f"index {index} out of range 0..{self._size - 1}")

    def add(self, index: int, delta: object) -> None:
        self._check(index)
        position = index + 1
        while position <= self._size:
            self._tree[position] += delta
            position += position & (-position)

    def prefix_sum(self, count: int) -> object:
        if not 0 <= count <= self._size:
            raise Invalid(f"prefix count {count} out of range 0..{self._size}")
        total = 0
        position = count
        while position > 0:
            total += self._tree[position]
            position -= position & (-position)
        return total

    def range_sum(self, low: int, high: int) -> object:
        if not 0 <= low <= high <= self._size:
            raise Invalid(f"range {low}..{high} out of bounds")
        return self.prefix_sum(high) - self.prefix_sum(low)

    def value(self, index: int) -> object:
        self._check(index)
        return self.range_sum(index, index + 1)

    def set(self, index: int, value: object) -> None:
        self._check(index)
        self.add(index, value - self.value(index))
