"""BST: a binary search tree keeping values sorted for ordered traversal and range.

A binary search tree stores values so that at every node the
left subtree holds smaller values and the right subtree larger,
which is the invariant that makes an in-order walk visit them
sorted and a search follow one path down rather than scan them
all. Inserting places a value by walking down from the root,
going left or right by comparison until it finds the empty spot
where the value belongs, and a value already present is not
inserted twice, so the tree holds a set of values in sorted
structure. The in-order traversal, left then node then right,
reads the values in order, which is how the tree doubles as a
sorted view without a separate sort, and the minimum and maximum
are the leftmost and rightmost nodes, found by walking one
direction to the end. The honest caveat is the one every plain
BST carries: inserting values in sorted order builds a tree that
is really a list, one long branch, and then its operations
degrade to linear, so this is the clear unbalanced tree that is
fast on random insertion order and slow on sorted, and a caller
needing the guarantee on any order wants a self-balancing tree,
an AVL or red-black, which keeps the height logarithmic at the
cost of rotations this does not do. Named rather than hidden,
because a caller feeding sorted data to a plain BST and
expecting logarithmic operations has a performance bug the tree
will not announce. For its common use, holding values inserted
in no particular order and reading them sorted, it is exactly
the simple structure that fits.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Invalid


@dataclass
class _Node:
    value: object
    left: _Node | None = None
    right: _Node | None = None


@dataclass
class BST:
    root: _Node | None = None
    size: int = 0

    def insert(self, value) -> None:
        self.root = self._insert(self.root, value)

    def _insert(self, node: _Node | None, value) -> _Node:
        if node is None:
            self.size += 1
            return _Node(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        return node

    def contains(self, value) -> bool:
        node = self.root
        while node is not None:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False

    def in_order(self) -> list:
        result: list = []

        def walk(node: _Node | None) -> None:
            if node is None:
                return
            walk(node.left)
            result.append(node.value)
            walk(node.right)

        walk(self.root)
        return result

    def minimum(self):
        if self.root is None:
            raise Invalid("an empty tree has no minimum")
        node = self.root
        while node.left is not None:
            node = node.left
        return node.value

    def maximum(self):
        if self.root is None:
            raise Invalid("an empty tree has no maximum")
        node = self.root
        while node.right is not None:
            node = node.right
        return node.value

    def __len__(self) -> int:
        return self.size


def of(values: list) -> BST:
    tree = BST()
    for value in values:
        tree.insert(value)
    return tree
