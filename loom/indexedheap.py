"""Indexedheap: a min-priority queue that can reach in and lower a key already inside it.

A binary heap makes a fine priority queue for pushing items and
popping the smallest, but it cannot find an item that is already
inside it, because a heap only knows its minimum, not where any
particular element sits. That matters the moment an algorithm needs
to lower the priority of something already queued, which Dijkstra's
shortest paths does every time it finds a cheaper route to a node
still waiting. I had assumed a plain heap was enough and the lower
was a detail; it is not reachable in a plain heap, and the common
workaround is to push a second copy of the item with its new lower
priority and ignore the stale copy when it later pops. That works
and is often good enough, but it lets the heap fill with corpses,
outdated entries that pop and get discarded, so the heap grows to
the number of updates rather than the number of live items. An
indexed heap fixes that by keeping a map alongside the heap from
each item to the slot it occupies, updated on every swap, so it can
locate any item in constant time and sift it up in place when its
priority drops. The price is that map, an extra dictionary touched
on every push, pop, and swap, and in return the heap stays exactly
the size of the live set with no stale entries, and the lower-a-key
operation the plain heap could not do at all becomes a sift from a
known position. The lower is guarded to actually be a lowering,
since raising a key would need a sift the other direction and
silently accepting it under a decrease-key name would corrupt the
order; an attempt to raise is refused rather than mishandled, and
popping an empty queue or pushing an item already present is
refused too rather than quietly corrupting the map.
"""

from __future__ import annotations

from loom.errors import Invalid


class IndexedHeap:
    __slots__ = ("_heap", "_position", "_priority")

    def __init__(self) -> None:
        self._heap: list = []
        self._priority: dict = {}
        self._position: dict = {}

    def __len__(self) -> int:
        return len(self._heap)

    def __contains__(self, item: object) -> bool:
        return item in self._position

    def priority(self, item: object) -> object:
        return self._priority[item]

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._position[self._heap[i]] = i
        self._position[self._heap[j]] = j

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._priority[self._heap[index]] < self._priority[self._heap[parent]]:
                self._swap(index, parent)
                index = parent
            else:
                break

    def _sift_down(self, index: int) -> None:
        size = len(self._heap)
        while True:
            smallest = index
            for child in (2 * index + 1, 2 * index + 2):
                if (
                    child < size
                    and self._priority[self._heap[child]]
                    < self._priority[self._heap[smallest]]
                ):
                    smallest = child
            if smallest == index:
                break
            self._swap(index, smallest)
            index = smallest

    def push(self, item: object, priority: object) -> None:
        if item in self._position:
            raise Invalid(f"{item!r} is already queued; use decrease_key to lower it")
        self._heap.append(item)
        self._priority[item] = priority
        self._position[item] = len(self._heap) - 1
        self._sift_up(len(self._heap) - 1)

    def peek(self) -> object:
        if not self._heap:
            raise Invalid("the queue is empty")
        return self._heap[0]

    def pop_min(self) -> object:
        if not self._heap:
            raise Invalid("the queue is empty")
        top = self._heap[0]
        last = self._heap.pop()
        del self._position[top]
        del self._priority[top]
        if self._heap:
            self._heap[0] = last
            self._position[last] = 0
            self._sift_down(0)
        return top

    def decrease_key(self, item: object, priority: object) -> None:
        if item not in self._position:
            raise Invalid(f"{item!r} is not in the queue")
        if priority > self._priority[item]:
            raise Invalid("decrease_key cannot raise a priority")
        self._priority[item] = priority
        self._sift_up(self._position[item])

    def push_or_decrease(self, item: object, priority: object) -> None:
        if item in self._position:
            if priority < self._priority[item]:
                self.decrease_key(item, priority)
        else:
            self.push(item, priority)
