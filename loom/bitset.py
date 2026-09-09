"""Bit set: a set of small non-negative integers packed into one integer's bits.

A set of small integers can live in the bits of a single
integer, member n being bit n, and this wraps that
representation into a set with the operations that follow from
it cheaply. Adding sets a bit, removing clears one, and
membership tests one, each a single bit operation, and the set
operations are the bitwise ones: union is or, intersection is
and, difference is and-not, so combining two sets is one
machine operation on their backing integers rather than a walk
over their elements, which is the whole reason to use a bit set
where the members are small and dense. The count of members is
the population count of the backing integer, the number of set
bits, and the members list reads them out in order. Python's
integers grow without bound, so the set is not limited to a
machine word; a member of a thousand simply sets the thousandth
bit, which means this stays correct where a fixed-width bit set
would overflow, at the cost of the space a large sparse member
costs, a bit set holding only the number one million uses a
million bits. That trade is the bit set's nature and named: it
is the right structure for many small dense integers and the
wrong one for a few enormous ones, where a hash set holds the
same members in a fraction of the space. Negative members are
refused, because a negative has no bit position and admitting
one would need a sign convention the structure does not have.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Invalid


@dataclass
class BitSet:
    bits: int = 0

    def add(self, member: int) -> BitSet:
        if member < 0:
            raise Invalid("a bit set holds non-negative integers")
        self.bits |= 1 << member
        return self

    def remove(self, member: int) -> BitSet:
        if member >= 0:
            self.bits &= ~(1 << member)
        return self

    def contains(self, member: int) -> bool:
        return member >= 0 and bool((self.bits >> member) & 1)

    def union(self, other: BitSet) -> BitSet:
        return BitSet(self.bits | other.bits)

    def intersection(self, other: BitSet) -> BitSet:
        return BitSet(self.bits & other.bits)

    def difference(self, other: BitSet) -> BitSet:
        return BitSet(self.bits & ~other.bits)

    def count(self) -> int:
        return bin(self.bits).count("1")

    def members(self) -> list[int]:
        return [
            index
            for index in range(self.bits.bit_length())
            if (self.bits >> index) & 1
        ]

    def __len__(self) -> int:
        return self.count()

    def __contains__(self, member: int) -> bool:
        return self.contains(member)


def of(members: list[int]) -> BitSet:
    result = BitSet()
    for member in members:
        result.add(member)
    return result
