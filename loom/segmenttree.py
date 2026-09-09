"""Segment tree: range queries and point updates over any associative combine, in a flat array.

A segment tree answers a question about a range of the data, the
sum or the smallest or the largest across positions from here to
there, and lets a single position change, both in the logarithm of
the length. It works by storing, above the data, the answer for
larger and larger blocks: the bottom row is the elements
themselves, and each row above holds, in each slot, the combined
answer for the two slots below it, so the top slot holds the
answer for the whole array and every slot in between holds the
answer for the contiguous block it covers. A query for an
arbitrary range climbs from the two ends of the range inward,
taking a block into the answer whenever that block lies wholly
inside the range and cannot be merged with its sibling without
spilling outside it, which happens a bounded number of times per
level, so the range is covered by a logarithmic number of stored
blocks rather than by scanning it. An update changes the leaf and
then walks straight up to the root, refreshing each parent from
its two children, again a logarithmic path. The combine can be any
operation that is associative, because the tree groups the range
into blocks and merges them, and as long as regrouping does not
change the result the answer is the same; it need not be
commutative, since the climb keeps the left contributions and the
right contributions in order and merges them on their correct
sides, which is what lets the same structure carry string
concatenation as easily as addition. I had guessed a segment tree
had to be recursive, a tree of node objects each splitting its
span at the midpoint; it does not, the whole thing fits in a flat
array of twice the length with the leaves in the second half and
every internal slot the combine of its two children, and the query
and the update are loops climbing that array by halving an index,
no recursion and no nodes. This is the structure the Fenwick tree
could not replace, because the Fenwick trick rests on subtracting
one prefix from another and the smallest of a range does not
subtract, so a range minimum needs the blocks kept whole, which is
exactly what this keeps.
"""

from __future__ import annotations

from collections.abc import Callable

from loom.errors import Invalid


class SegmentTree:
    __slots__ = ("_combine", "_identity", "_size", "_tree")

    def __init__(
        self,
        values: list,
        combine: Callable[[object, object], object],
        identity: object,
    ) -> None:
        self._combine = combine
        self._identity = identity
        self._size = len(values)
        self._tree = [identity] * (2 * self._size)
        for index, value in enumerate(values):
            self._tree[self._size + index] = value
        for index in range(self._size - 1, 0, -1):
            self._tree[index] = combine(
                self._tree[2 * index], self._tree[2 * index + 1]
            )

    @classmethod
    def for_sum(cls, values: list) -> SegmentTree:
        return cls(values, lambda a, b: a + b, 0)

    @classmethod
    def for_min(cls, values: list) -> SegmentTree:
        return cls(values, min, float("inf"))

    @classmethod
    def for_max(cls, values: list) -> SegmentTree:
        return cls(values, max, float("-inf"))

    def __len__(self) -> int:
        return self._size

    def update(self, index: int, value: object) -> None:
        if not 0 <= index < self._size:
            raise Invalid(f"index {index} out of range 0..{self._size - 1}")
        position = index + self._size
        self._tree[position] = value
        position //= 2
        while position >= 1:
            self._tree[position] = self._combine(
                self._tree[2 * position], self._tree[2 * position + 1]
            )
            position //= 2

    def query(self, low: int, high: int) -> object:
        if not 0 <= low <= high <= self._size:
            raise Invalid(f"range {low}..{high} out of bounds")
        left = self._identity
        right = self._identity
        low += self._size
        high += self._size
        while low < high:
            if low & 1:
                left = self._combine(left, self._tree[low])
                low += 1
            if high & 1:
                high -= 1
                right = self._combine(self._tree[high], right)
            low //= 2
            high //= 2
        return self._combine(left, right)

    def value(self, index: int) -> object:
        if not 0 <= index < self._size:
            raise Invalid(f"index {index} out of range 0..{self._size - 1}")
        return self._tree[index + self._size]
