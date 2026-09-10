"""Treap: an ordered set balanced by random priorities, a tree and a heap at once.

A treap is a binary search tree in its keys and, at the same time,
a heap in a second field it gives each node: a random priority. It
keeps two orderings that pull in different directions, keys sorted
left to right as in any search tree, and priorities arranged so that
every node's priority is at least its children's, as in a heap, and
it maintains both at once through rotations. When an insert would
put a node below a parent of lower priority, a rotation lifts the
higher-priority node up without disturbing the key order, and
rotations repeat until the heap order is restored, which never takes
more than the height. The point of the priorities is balance. I had
guessed a tree left to random chance could not be trusted to stay
short the way an AVL tree, which explicitly measures and rebalances,
can; the priorities make the treap's shape identical to the shape a
plain search tree would take if the keys had been inserted in the
order of their priorities, and since the priorities are random that
order is a random order, whose expected height is logarithmic. So
the balance comes for free from the priorities being independent of
the keys, with no height ever measured and no subtree ever counted,
which is the surprising economy: the same expected balance as the
explicit balancer, bought with a random number per node instead of
bookkeeping per change. The honest catch is that it is expected, not
guaranteed; an unlucky draw of priorities could build a tall tree,
just as an unlucky insertion order could, and the defence is only
that the draw is random so no particular set of keys can force the
bad case. The priority source is seedable so the same keys build the
same tree and the shape can be tested, and this holds keys as a set,
reinserting one changing nothing, reading them back sorted by the
in-order walk any search tree gives.
"""

from __future__ import annotations

import random


class _Node:
    __slots__ = ("key", "left", "priority", "right")

    def __init__(self, key: object, priority: float) -> None:
        self.key = key
        self.priority = priority
        self.left: _Node | None = None
        self.right: _Node | None = None


def _rotate_right(root: _Node) -> _Node:
    pivot = root.left
    root.left = pivot.right
    pivot.right = root
    return pivot


def _rotate_left(root: _Node) -> _Node:
    pivot = root.right
    root.right = pivot.left
    pivot.left = root
    return pivot


class Treap:
    __slots__ = ("_rng", "_root", "_size")

    def __init__(self, seed: int | None = None) -> None:
        self._root: _Node | None = None
        self._size = 0
        self._rng = random.Random(seed)

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: object) -> bool:
        node = self._root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def insert(self, key: object) -> bool:
        before = self._size
        self._root = self._insert(self._root, key)
        return self._size > before

    def _insert(self, node: _Node | None, key: object) -> _Node:
        if node is None:
            self._size += 1
            return _Node(key, self._rng.random())
        if key == node.key:
            return node
        if key < node.key:
            node.left = self._insert(node.left, key)
            if node.left.priority > node.priority:
                node = _rotate_right(node)
        else:
            node.right = self._insert(node.right, key)
            if node.right.priority > node.priority:
                node = _rotate_left(node)
        return node

    def remove(self, key: object) -> bool:
        if key not in self:
            return False
        self._root = self._remove(self._root, key)
        self._size -= 1
        return True

    def _remove(self, node: _Node | None, key: object) -> _Node | None:
        if key < node.key:
            node.left = self._remove(node.left, key)
            return node
        if key > node.key:
            node.right = self._remove(node.right, key)
            return node
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        if node.left.priority > node.right.priority:
            node = _rotate_right(node)
            node.right = self._remove(node.right, key)
        else:
            node = _rotate_left(node)
            node.left = self._remove(node.left, key)
        return node

    def items(self) -> list:
        out: list = []
        self._walk(self._root, out)
        return out

    def _walk(self, node: _Node | None, out: list) -> None:
        if node is None:
            return
        self._walk(node.left, out)
        out.append(node.key)
        self._walk(node.right, out)

    def is_heap_ordered(self) -> bool:
        return self._check(self._root)

    def _check(self, node: _Node | None) -> bool:
        for child in (node.left, node.right) if node is not None else ():
            if child is not None and (child.priority > node.priority or not self._check(child)):
                return False
        return True
