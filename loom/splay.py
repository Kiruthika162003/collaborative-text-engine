"""Splay tree: a search tree with no balance information that rotates each touch to the root.

A splay tree is a binary search tree with one move: whenever a key
is looked up, inserted, or deleted, the tree rotates that key up
step by step until it becomes the root, a maneuver called splaying.
It keeps no heights, no colors, no priorities, none of the balance
information the other self-balancing trees carry, and it never
measures a subtree; the only thing it ever does is splay the node
it just touched to the top. That sounds like it could not possibly
stay efficient, and taken one operation at a time it does not: a
single lookup on an unlucky tree can walk a long thin path and cost
the whole length. I had guessed that ruled it out against a tree
that explicitly rebalances. It does not, because the guarantee a
splay tree offers is amortized rather than per-operation: over any
sequence of operations the total cost is logarithmic per operation
even though individual ones can be worse, since an expensive splay
that climbs a long path also flattens that path, paying for itself
by making the next operations cheap. And splaying brings a bonus
the balanced trees do not have. Because every touched key is left
sitting at the root, the keys touched most recently are the
cheapest to reach, so a workload that returns to the same handful
of keys again and again runs faster than logarithmic, the tree
quietly shaping itself to the access pattern for free. That is the
honest reason to reach for it over an AVL tree, self-adjustment to
the workload and no per-node bookkeeping, accepted against a worse
single-operation worst case. The splaying here is the top-down
form, assembling the two sides of the tree as it descends rather
than recursing down and rotating back up, so no operation recurses
and a deep transient tree cannot overflow the call stack, and it
holds keys as a set read back in order by an in-order walk.
"""

from __future__ import annotations


class _Node:
    __slots__ = ("key", "left", "right")

    def __init__(self, key: object) -> None:
        self.key = key
        self.left: _Node | None = None
        self.right: _Node | None = None


def _splay(root: _Node, key: object) -> _Node:
    dummy = _Node(None)
    left_tail = dummy
    right_head = dummy
    node = root
    while True:
        if key < node.key:
            if node.left is None:
                break
            if key < node.left.key:
                pivot = node.left
                node.left = pivot.right
                pivot.right = node
                node = pivot
                if node.left is None:
                    break
            right_head.left = node
            right_head = node
            node = node.left
        elif key > node.key:
            if node.right is None:
                break
            if key > node.right.key:
                pivot = node.right
                node.right = pivot.left
                pivot.left = node
                node = pivot
                if node.right is None:
                    break
            left_tail.right = node
            left_tail = node
            node = node.right
        else:
            break
    left_tail.right = node.left
    right_head.left = node.right
    node.left = dummy.right
    node.right = dummy.left
    return node


class SplayTree:
    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: object) -> bool:
        if self._root is None:
            return False
        self._root = _splay(self._root, key)
        return self._root.key == key

    def insert(self, key: object) -> bool:
        if self._root is None:
            self._root = _Node(key)
            self._size += 1
            return True
        self._root = _splay(self._root, key)
        if self._root.key == key:
            return False
        fresh = _Node(key)
        if key < self._root.key:
            fresh.right = self._root
            fresh.left = self._root.left
            self._root.left = None
        else:
            fresh.left = self._root
            fresh.right = self._root.right
            self._root.right = None
        self._root = fresh
        self._size += 1
        return True

    def remove(self, key: object) -> bool:
        if self._root is None:
            return False
        self._root = _splay(self._root, key)
        if self._root.key != key:
            return False
        left = self._root.left
        right = self._root.right
        if left is None:
            self._root = right
        else:
            left = _splay(left, key)
            left.right = right
            self._root = left
        self._size -= 1
        return True

    def items(self) -> list:
        out: list = []
        stack: list = []
        node = self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            out.append(node.key)
            node = node.right
        return out
