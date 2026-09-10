"""Hashmap: a dictionary from scratch by open addressing, where deletion must leave a tombstone.

This is a hash table built by open addressing: every key lives
directly in the slot array rather than in a list hanging off a
bucket. A key's home slot is its hash reduced to the array size,
and when that slot is taken by a different key the table probes
forward one slot at a time until it finds the key or an empty slot,
which is linear probing. Insertion walks that probe sequence to the
first place the key can go, lookup walks it until the key turns up
or an empty slot proves it absent, and the table grows and rehashes
everything when it fills past a threshold, because probe sequences
lengthen sharply as a table nears full and a half-empty table keeps
them short. The subtlety, and the thing I got wrong first, is
deletion. I had assumed removing a key was just blanking its slot;
it is not, and blanking breaks the table. A key that collided with
the deleted one may have been placed further along its probe
sequence, past the slot now blanked, and a later lookup for that
key walks from its home slot and stops at the first empty slot it
meets, so a freshly blanked slot in the middle of a probe sequence
makes the lookup stop early and declare a key absent that is
sitting right there. Deletion therefore leaves a tombstone, a
marker that means occupied-for-probing but available-for-insertion:
lookups treat it as a filled slot and keep walking past it, so the
probe sequence stays intact, while insertions may reclaim it. The
cost is that tombstones accumulate and lengthen probes even as live
entries leave, so the table has to count tombstones toward its load
and rebuild to sweep them out, not just count the keys that remain,
which is the honest price of open addressing's deletion. The array
size is kept a power of two so the hash reduces to a slot by a
bitmask rather than a division, and it matches a real dictionary
over inserts, updates, deletes, and lookups.
"""

from __future__ import annotations

_EMPTY = object()
_DELETED = object()


class HashMap:
    __slots__ = ("_capacity", "_keys", "_size", "_used", "_vals")

    def __init__(self, capacity: int = 8) -> None:
        self._capacity = 8
        while self._capacity < capacity:
            self._capacity *= 2
        self._keys: list = [_EMPTY] * self._capacity
        self._vals: list = [None] * self._capacity
        self._size = 0
        self._used = 0

    def __len__(self) -> int:
        return self._size

    def _slot_for(self, key: object) -> int:
        mask = self._capacity - 1
        index = hash(key) & mask
        first_deleted = -1
        while True:
            occupant = self._keys[index]
            if occupant is _EMPTY:
                return index if first_deleted < 0 else first_deleted
            if occupant is _DELETED:
                if first_deleted < 0:
                    first_deleted = index
            elif occupant == key:
                return index
            index = (index + 1) & mask

    def _is_live(self, occupant: object) -> bool:
        return occupant is not _EMPTY and occupant is not _DELETED

    def __setitem__(self, key: object, value: object) -> None:
        index = self._slot_for(key)
        occupant = self._keys[index]
        if self._is_live(occupant):
            self._vals[index] = value
            return
        if occupant is _EMPTY:
            self._used += 1
        self._keys[index] = key
        self._vals[index] = value
        self._size += 1
        if self._used * 3 >= self._capacity * 2:
            self._resize(self._capacity * 2)

    def __getitem__(self, key: object) -> object:
        index = self._slot_for(key)
        if self._is_live(self._keys[index]):
            return self._vals[index]
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        return self._is_live(self._keys[self._slot_for(key)])

    def get(self, key: object, default: object = None) -> object:
        index = self._slot_for(key)
        return self._vals[index] if self._is_live(self._keys[index]) else default

    def __delitem__(self, key: object) -> None:
        index = self._slot_for(key)
        if not self._is_live(self._keys[index]):
            raise KeyError(key)
        self._keys[index] = _DELETED
        self._vals[index] = None
        self._size -= 1

    def _resize(self, capacity: int) -> None:
        old_keys = self._keys
        old_vals = self._vals
        self._capacity = capacity
        self._keys = [_EMPTY] * capacity
        self._vals = [None] * capacity
        self._size = 0
        self._used = 0
        for key, value in zip(old_keys, old_vals, strict=True):
            if self._is_live(key):
                self[key] = value

    def keys(self) -> list:
        return [key for key in self._keys if self._is_live(key)]

    def items(self) -> list:
        return [
            (key, self._vals[index])
            for index, key in enumerate(self._keys)
            if self._is_live(key)
        ]
