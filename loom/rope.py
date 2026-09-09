"""Rope: a document held as a tree of small string pieces, joined and split by the branch.

A rope stores text not as one long string but as the leaves of a
binary tree, each leaf a short piece of the document and each
branch remembering the total length of everything in its left
subtree. Reading the document is an in-order walk gathering the
leaves left to right, and finding the character at a position
walks down from the root choosing left or right by comparing the
position against that stored left-length, so a lookup costs the
depth of the tree rather than a scan. The point of the shape is
what it makes cheap. Joining two ropes is a single new branch
over the two roots, no character copied, and splitting a rope at
a position walks down to that spot and hands back the two sides
as their own trees, again copying nothing but the handful of
branches along the path. Insert and delete are then just split
and join: to insert, split at the point, join the left, the new
piece, and the right; to delete a range, split twice and join the
two outer pieces past the hole. Each of those touches only the
nodes on a root-to-leaf path, so on a balanced tree an edit
anywhere costs the depth, which grows with the logarithm of the
length, not the length. I had guessed a rope would only earn its
keep on enormous documents, that for anything smaller the plain
string would win; the edit cost really is logarithmic in the
balanced case, so an insert far from the end is cheap even at
modest sizes, which surprised me. The catch is the balance. A
long run of joins without rebalancing grows the tree lopsided,
each join adding a level down one side, until lookups and edits
degrade toward walking a list, so the structure keeps a rebalance
that gathers the leaves and rebuilds the tree even, trading a
one-time full pass for restored logarithmic edits. Tiny adjacent
leaves are merged when they join, to keep the tree from filling
with slivers, which is the counterpart of the split that made
them. Against the piece table and the gap buffer this is the
persistent one: split and join make new trees over shared
subtrees rather than mutating a buffer in place, so an old version
stays valid after an edit, which is the property a rope is really
reached for.
"""

from __future__ import annotations

from loom.errors import Invalid

LEAF_MAX = 16


class _Leaf:
    __slots__ = ("length", "text")

    def __init__(self, text: str) -> None:
        self.text = text
        self.length = len(text)


class _Branch:
    __slots__ = ("left", "length", "right", "weight")

    def __init__(self, left: object, right: object) -> None:
        self.left = left
        self.right = right
        self.weight = _length(left)
        self.length = self.weight + _length(right)


def _length(node: object) -> int:
    return 0 if node is None else node.length


def _leaf_or_none(text: str) -> object:
    return _Leaf(text) if text else None


def _build(text: str) -> object:
    if text == "":
        return None
    leaves = [_Leaf(text[i : i + LEAF_MAX]) for i in range(0, len(text), LEAF_MAX)]
    while len(leaves) > 1:
        leaves = [
            _Branch(leaves[i], leaves[i + 1]) if i + 1 < len(leaves) else leaves[i]
            for i in range(0, len(leaves), 2)
        ]
    return leaves[0]


def _concat(left: object, right: object) -> object:
    if left is None:
        return right
    if right is None:
        return left
    if (
        isinstance(left, _Leaf)
        and isinstance(right, _Leaf)
        and left.length + right.length <= LEAF_MAX
    ):
        return _Leaf(left.text + right.text)
    return _Branch(left, right)


def _split(node: object, offset: int) -> tuple[object, object]:
    if node is None:
        return None, None
    if isinstance(node, _Leaf):
        return _leaf_or_none(node.text[:offset]), _leaf_or_none(node.text[offset:])
    if offset < node.weight:
        left, right = _split(node.left, offset)
        return left, _concat(right, node.right)
    left, right = _split(node.right, offset - node.weight)
    return _concat(node.left, left), right


def _char_at(node: object, offset: int) -> str:
    while isinstance(node, _Branch):
        if offset < node.weight:
            node = node.left
        else:
            offset -= node.weight
            node = node.right
    return node.text[offset]


def _collect(node: object, parts: list) -> None:
    if node is None:
        return
    if isinstance(node, _Leaf):
        parts.append(node.text)
        return
    _collect(node.left, parts)
    _collect(node.right, parts)


def _depth(node: object) -> int:
    if node is None or isinstance(node, _Leaf):
        return 1
    return 1 + max(_depth(node.left), _depth(node.right))


class Rope:
    __slots__ = ("_root",)

    def __init__(self, text: str = "") -> None:
        self._root = _build(text)

    @classmethod
    def _wrap(cls, node: object) -> Rope:
        rope = cls.__new__(cls)
        rope._root = node
        return rope

    def __len__(self) -> int:
        return _length(self._root)

    def text(self) -> str:
        parts: list[str] = []
        _collect(self._root, parts)
        return "".join(parts)

    def char_at(self, offset: int) -> str:
        if not 0 <= offset < len(self):
            raise Invalid(f"index {offset} out of range")
        return _char_at(self._root, offset)

    def concat(self, other: Rope) -> Rope:
        return Rope._wrap(_concat(self._root, other._root))

    def split(self, offset: int) -> tuple[Rope, Rope]:
        if not 0 <= offset <= len(self):
            raise Invalid(f"split offset {offset} out of range")
        left, right = _split(self._root, offset)
        return Rope._wrap(left), Rope._wrap(right)

    def insert(self, offset: int, text: str) -> Rope:
        if not 0 <= offset <= len(self):
            raise Invalid(f"insert offset {offset} out of range")
        left, right = _split(self._root, offset)
        self._root = _concat(_concat(left, _build(text)), right)
        return self

    def delete(self, offset: int, length: int) -> Rope:
        if length < 0:
            raise Invalid("delete length is negative")
        if not 0 <= offset <= len(self) - length:
            raise Invalid(f"delete range {offset}..{offset + length} out of bounds")
        left, rest = _split(self._root, offset)
        _, right = _split(rest, length)
        self._root = _concat(left, right)
        return self

    def substring(self, offset: int, length: int) -> str:
        if length < 0:
            raise Invalid("substring length is negative")
        if not 0 <= offset <= len(self) - length:
            raise Invalid(f"substring range {offset}..{offset + length} out of bounds")
        return self.text()[offset : offset + length]

    def depth(self) -> int:
        return _depth(self._root)

    def rebalance(self) -> Rope:
        self._root = _build(self.text())
        return self
