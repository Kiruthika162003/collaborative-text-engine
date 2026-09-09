"""Ring buffer: a fixed-capacity queue that keeps only the most recent entries.

A ring buffer holds a bounded window of the most recent items,
dropping the oldest to make room when it fills, which is what a
recent-history log or a moving window over a stream needs. It
fills up to its capacity like an ordinary list, and once full a
push overwrites the oldest slot and advances a start pointer, so
the buffer always holds the last capacity items and the memory
never grows past that bound however long the stream runs, which
is the whole point over an unbounded list that would keep every
item forever. Reading the items back gives them oldest to
newest regardless of where the physical start has rotated to,
by reading from the start pointer around to it, so a caller sees
a clean chronological window without knowing the buffer wrapped.
The overwrite is silent by design, because a ring buffer's
contract is that old items fall off the end, and warning about
each dropped item would defeat the point of a structure whose
job is to forget the old; a caller who must not lose items wants
an unbounded queue, not this. The capacity is fixed at
construction and must be at least one, since a buffer of zero
capacity holds nothing and every push would drop immediately,
which is a bug in the capacity rather than a use. It stores any
items a caller pushes, holding no opinion about them, and the
oldest-to-newest ordering is the only structure it imposes,
because recency is the one thing a ring buffer is about.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid


@dataclass
class RingBuffer:
    capacity: int
    _data: list = field(default_factory=list)
    _start: int = 0

    def __post_init__(self) -> None:
        if self.capacity < 1:
            raise Invalid("a ring buffer needs room for at least one item")

    def push(self, item) -> None:
        if len(self._data) < self.capacity:
            self._data.append(item)
        else:
            self._data[self._start] = item
            self._start = (self._start + 1) % self.capacity

    def items(self) -> list:
        if len(self._data) < self.capacity:
            return list(self._data)
        return self._data[self._start :] + self._data[: self._start]

    def is_full(self) -> bool:
        return len(self._data) == self.capacity

    def __len__(self) -> int:
        return len(self._data)
