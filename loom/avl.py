"""AVL tree: an ordered set that rebalances on every change so it can never grow into a chain.

A binary search tree keeps keys ordered so a lookup walks down
from the root choosing left or right, which is fast only while the
tree stays short. Insert keys in sorted order into a plain search
tree and it degenerates into a chain, every node hanging off the
right of the last, and the lookup that was supposed to cost the
height now costs the length. An AVL tree forbids that by keeping a
promise at every node: the heights of its two subtrees differ by
at most one. Each insert and each delete walks back up the path it
came down, refreshing heights, and wherever the promise has been
broken it rotates, a local rearrangement of a node and its child
that shortens the tall side and lengthens the short one without
disturbing the ordering. There are four shapes of imbalance and
they reduce to two rotations, one to the left and one to the
right, applied singly or in pairs, and each is a handful of
pointer moves that runs in constant time. Because a rotation is
constant and the walk back up is the height, and the height is
kept logarithmic, a change costs the logarithm even in the sorted
insertion case that ruins the plain tree. I had guessed the
balancing would cost more than it saved, that rotating on every
insert would outweigh the shorter searches it bought; it does not,
because the rotations are constant and there are at most a couple
per change, while the alternative is not a slightly taller tree but
a chain, the degenerate case that turns every later operation
linear. So the balancing is not a refinement for its own sake but
insurance against the input that actually arrives sorted, which is
common enough, a log imported in order, that the plain tree cannot
be trusted with it. This holds keys as a set, so inserting a key
already present changes nothing, and it reads back in order by an
in-order walk, the sorted sequence being the one thing a search
tree gives for free.
"""

from __future__ import annotations


class _Node:
    __slots__ = ("height", "key", "left", "right")

    def __init__(self, key: object) -> None:
        self.key = key
        self.left: _Node | None = None
        self.right: _Node | None = None
        self.height = 1


def _height(node: _Node | None) -> int:
    return 0 if node is None else node.height


def _balance_factor(node: _Node | None) -> int:
    if node is None:
        return 0
    return _height(node.left) - _height(node.right)


def _reheight(node: _Node) -> None:
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_right(root: _Node) -> _Node:
    pivot = root.left
    root.left = pivot.right
    pivot.right = root
    _reheight(root)
    _reheight(pivot)
    return pivot


def _rotate_left(root: _Node) -> _Node:
    pivot = root.right
    root.right = pivot.left
    pivot.left = root
    _reheight(root)
    _reheight(pivot)
    return pivot


def _rebalance(node: _Node) -> _Node:
    _reheight(node)
    balance = _balance_factor(node)
    if balance > 1:
        if _balance_factor(node.left) < 0:
            node.left = _rotate_left(node.left)
        return _rotate_right(node)
    if balance < -1:
        if _balance_factor(node.right) > 0:
            node.right = _rotate_right(node.right)
        return _rotate_left(node)
    return node


def _min_node(node: _Node) -> _Node:
    while node.left is not None:
        node = node.left
    return node


class AVLTree:
    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: _Node | None = None
        self._size = 0

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
            return _Node(key)
        if key == node.key:
            return node
        if key < node.key:
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)
        return _rebalance(node)

    def remove(self, key: object) -> bool:
        before = self._size
        self._root = self._remove(self._root, key)
        return self._size < before

    def _remove(self, node: _Node | None, key: object) -> _Node | None:
        if node is None:
            return None
        if key < node.key:
            node.left = self._remove(node.left, key)
        elif key > node.key:
            node.right = self._remove(node.right, key)
        else:
            self._size -= 1
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = _min_node(node.right)
            node.key = successor.key
            self._size += 1
            node.right = self._remove(node.right, successor.key)
        return _rebalance(node)

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

    def minimum(self) -> object:
        if self._root is None:
            raise ValueError("an empty tree has no minimum")
        return _min_node(self._root).key

    def maximum(self) -> object:
        if self._root is None:
            raise ValueError("an empty tree has no maximum")
        node = self._root
        while node.right is not None:
            node = node.right
        return node.key

    def height(self) -> int:
        return _height(self._root)

    def is_balanced(self) -> bool:
        return self._check(self._root)

    def _check(self, node: _Node | None) -> bool:
        if node is None:
            return True
        if abs(_balance_factor(node)) > 1:
            return False
        return self._check(node.left) and self._check(node.right)
