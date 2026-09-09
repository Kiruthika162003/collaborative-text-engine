"""Skip list: an ordered set kept fast by coin flips instead of rotations.

A sorted linked list finds a key by walking it one node at a
time, which is slow because it has no way to skip ahead. A skip
list gives it express lanes. Every node sits on the bottom lane, a
plain sorted chain, and each node is also promoted to some number
of higher lanes decided by flipping a coin: about half the nodes
reach the second lane, about a quarter the third, and so on, so
the higher lanes are sparse and span long distances in a single
link. A search starts on the highest lane and runs forward until
the next node would overshoot the target, then drops down a lane
and continues, skipping over most of the list on the way down and
landing exactly where the key belongs. Because each lane roughly
halves the number of nodes, the drops number about the logarithm
of the length, so search, insert, and delete are logarithmic in
expectation. What surprised me is what holds that structure
together. I had guessed a skip list would need the careful
rebalancing an AVL tree does, that letting chance decide the lanes
would leave it lopsided and slow; it does not, because over many
independent coin flips the lane heights stay close enough to their
intended proportions that the express lanes remain useful without
any node ever being moved to fix them. That is the trade it makes
against the AVL tree: it gives up the tree's guarantee that the
height is always logarithmic and accepts instead a height that is
logarithmic in expectation, an unlucky run of flips could in
principle build a tall thin tower, and in return it is markedly
simpler, an insert splices a node into a few lanes and a delete
unsplices it, with none of the four rotation cases. On random keys
the two are equally quick, and the skip list is the one to reach
for when the simplicity of splice-and-unsplice matters more than a
hard worst-case bound. The coin is seedable here so the same
sequence of operations builds the same list, since a structure
whose shape depended on an unseen random source could not be
tested for the shape it actually built.
"""

from __future__ import annotations

import random

from loom.errors import Invalid


class _Node:
    __slots__ = ("forward", "key")

    def __init__(self, key: object, level: int) -> None:
        self.key = key
        self.forward: list = [None] * level


class SkipList:
    __slots__ = ("_head", "_level", "_max_level", "_probability", "_rng", "_size")

    def __init__(
        self,
        max_level: int = 16,
        probability: float = 0.5,
        seed: int | None = None,
    ) -> None:
        if max_level < 1:
            raise Invalid("a skip list needs at least one lane")
        self._max_level = max_level
        self._probability = probability
        self._head = _Node(None, max_level)
        self._level = 1
        self._size = 0
        self._rng = random.Random(seed)

    def __len__(self) -> int:
        return self._size

    def _random_level(self) -> int:
        level = 1
        while self._rng.random() < self._probability and level < self._max_level:
            level += 1
        return level

    def _predecessors(self, key: object) -> list:
        update: list = [self._head] * self._max_level
        node = self._head
        for lane in reversed(range(self._level)):
            while node.forward[lane] is not None and node.forward[lane].key < key:
                node = node.forward[lane]
            update[lane] = node
        return update

    def __contains__(self, key: object) -> bool:
        node = self._head
        for lane in reversed(range(self._level)):
            while node.forward[lane] is not None and node.forward[lane].key < key:
                node = node.forward[lane]
        landing = node.forward[0]
        return landing is not None and landing.key == key

    def insert(self, key: object) -> bool:
        update = self._predecessors(key)
        candidate = update[0].forward[0]
        if candidate is not None and candidate.key == key:
            return False
        level = self._random_level()
        if level > self._level:
            for lane in range(self._level, level):
                update[lane] = self._head
            self._level = level
        fresh = _Node(key, level)
        for lane in range(level):
            fresh.forward[lane] = update[lane].forward[lane]
            update[lane].forward[lane] = fresh
        self._size += 1
        return True

    def remove(self, key: object) -> bool:
        update = self._predecessors(key)
        target = update[0].forward[0]
        if target is None or target.key != key:
            return False
        for lane in range(self._level):
            if update[lane].forward[lane] is target:
                update[lane].forward[lane] = target.forward[lane]
        while self._level > 1 and self._head.forward[self._level - 1] is None:
            self._level -= 1
        self._size -= 1
        return True

    def items(self) -> list:
        out = []
        node = self._head.forward[0]
        while node is not None:
            out.append(node.key)
            node = node.forward[0]
        return out

    def level(self) -> int:
        return self._level
