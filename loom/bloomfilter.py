"""Bloom filter: a compact probabilistic set that never misses a member it holds.

A Bloom filter answers set membership in a fraction of the space
a real set would take, by accepting a controlled kind of error:
it may say a non-member is present, but it never says a member
is absent. Each item is hashed to several bit positions, and
adding it sets those bits; testing it checks whether all its
bits are set. A member's bits were set when it was added, so a
member always tests present, which is the guarantee that makes
the filter safe as a first pass, a cheap check that rules out
the definitely-absent before an expensive lookup. A non-member
tests present only if every one of its bits happens to have been
set by other items, which is the false positive, and its rate
rises as the filter fills, so the size and the number of hash
functions are chosen against the expected item count to keep it
low. The hashing is a deterministic pair combined by double
hashing, giving as many positions as wanted from two hashes, and
deterministic on purpose so the same items set the same bits on
every run, since a filter whose behaviour depended on a
randomized hash would give different false positives each run
and be impossible to reason about. The one thing it cannot do is
remove an item, because clearing its bits might clear a bit
another item needs, so a Bloom filter grows more false positives
as it fills and is rebuilt rather than pruned, which is its
nature and stated: it is the right structure for a membership
test that tolerates a rare false yes, and the wrong one where a
false yes is costly or where removal is needed.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Invalid

FNV_PRIME = 0x01000193
MASK = 0xFFFFFFFF


def _hash(data: bytes, seed: int) -> int:
    value = seed
    for byte in data:
        value = ((value ^ byte) * FNV_PRIME) & MASK
    return value


@dataclass
class BloomFilter:
    size: int
    hashes: int = 3
    bits: int = 0

    def __post_init__(self) -> None:
        if self.size < 1 or self.hashes < 1:
            raise Invalid("size and hash count must be positive")

    def _positions(self, item: str) -> list[int]:
        data = item.encode("utf-8")
        first = _hash(data, 0x811C9DC5)
        second = _hash(data, 0x01000193) or 1
        return [(first + index * second) % self.size for index in range(self.hashes)]

    def add(self, item: str) -> None:
        for position in self._positions(item):
            self.bits |= 1 << position

    def contains(self, item: str) -> bool:
        return all(
            (self.bits >> position) & 1 for position in self._positions(item)
        )

    def __contains__(self, item: str) -> bool:
        return self.contains(item)
