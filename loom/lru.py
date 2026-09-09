"""LRU cache: a fixed-size cache that evicts the least recently used entry.

A cache with a size limit has to choose what to drop when it
fills, and least-recently-used is the choice that assumes the
recent past predicts the near future: the entry untouched
longest is the one least likely to be wanted next. This
implements it on an insertion-ordered dictionary, where the
order of the keys is the order they were last used, oldest
first. A get moves its key to the most-recent end by removing
and reinserting it, so touching an entry refreshes it, and a
put adds or refreshes a key at that end and then, if the cache
is now over capacity, drops the key at the oldest end, which is
the first in iteration order. Both operations are constant time,
because the dictionary does the reordering in one removal and
one insertion rather than a scan for the oldest. A get on a
missing key returns a default rather than raising, since a
cache miss is the normal case a caller handles by computing the
value, not an error, and putting a key already present updates
its value and refreshes it rather than adding a duplicate. The
capacity is fixed at construction and must be at least one,
because a cache of zero entries caches nothing and is almost
always a bug in how the size was computed rather than a real
request. It caches whatever hashable keys and any values a
caller stores, holding no opinion about them, since a cache's
job is to remember and forget by recency and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid


@dataclass
class LRUCache:
    capacity: int
    store: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.capacity < 1:
            raise Invalid("a cache needs room for at least one entry")

    def get(self, key, default=None):
        if key not in self.store:
            return default
        value = self.store.pop(key)
        self.store[key] = value
        return value

    def put(self, key, value) -> None:
        if key in self.store:
            self.store.pop(key)
        self.store[key] = value
        if len(self.store) > self.capacity:
            oldest = next(iter(self.store))
            del self.store[oldest]

    def __contains__(self, key) -> bool:
        return key in self.store

    def __len__(self) -> int:
        return len(self.store)

    def keys(self) -> list:
        return list(self.store)
