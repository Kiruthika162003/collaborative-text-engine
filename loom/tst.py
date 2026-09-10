"""TST: a ternary search tree storing strings with three pointers a node, not one per letter.

A trie stores a set of strings by giving each node one child per
possible next character, so walking a string down the trie is a
direct index at each step, fast but wasteful: every node reserves a
slot for every character in the alphabet whether or not any string
uses it, which on a large alphabet with sparse branching spends far
more space than the strings themselves justify. A ternary search
tree keeps the same idea, a path spelling a string, but gives each
node only three pointers: one for characters less than the node's
own, one for greater, and one, the middle, for the next character
when this one matches. Searching compares the current character to
the node's character and goes less, greater, or, on a match, down
the middle to the next character of the key, so a step is a
comparison rather than an index. I had guessed the trie's slot per
character was necessary for the prefix queries to be fast; it is
not, the ternary tree answers the same queries and spends nodes in
proportion to the characters actually stored rather than to the
alphabet size, which is the trade it makes, a comparison per step
against a plain array lookup, for space that follows the data
instead of the alphabet. The structure earns its keep on the query
a plain hash set cannot answer, all keys sharing a prefix, because
the keys extending a prefix are exactly the middle subtree hanging
below where the prefix ends, so gathering them is one traversal of
that subtree, and because the less-equal-greater ordering is an
in-order arrangement the keys come out sorted for free. Storing the
empty string has no node to hang an end mark on, so it is refused
rather than silently mishandled, and every returned list of keys is
sorted, since a dictionary whose enumeration order wandered would
be a poor foundation for the completion and prefix features built
on it.
"""

from __future__ import annotations

from loom.errors import Invalid


class _Node:
    __slots__ = ("char", "eq", "hi", "is_end", "lo", "value")

    def __init__(self, char: str) -> None:
        self.char = char
        self.lo: _Node | None = None
        self.eq: _Node | None = None
        self.hi: _Node | None = None
        self.is_end = False
        self.value: object = None


def _collect(node: _Node | None, prefix: str, out: list) -> None:
    if node is None:
        return
    _collect(node.lo, prefix, out)
    if node.is_end:
        out.append(prefix + node.char)
    _collect(node.eq, prefix + node.char, out)
    _collect(node.hi, prefix, out)


class TernarySearchTree:
    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, key: str, value: object = True) -> None:
        if key == "":
            raise Invalid("a ternary search tree cannot store the empty string")
        self._root = self._insert(self._root, key, 0, value)

    def _insert(self, node: _Node | None, key: str, depth: int, value: object) -> _Node:
        char = key[depth]
        if node is None:
            node = _Node(char)
        if char < node.char:
            node.lo = self._insert(node.lo, key, depth, value)
        elif char > node.char:
            node.hi = self._insert(node.hi, key, depth, value)
        elif depth < len(key) - 1:
            node.eq = self._insert(node.eq, key, depth + 1, value)
        else:
            if not node.is_end:
                self._size += 1
            node.is_end = True
            node.value = value
        return node

    def _find(self, key: str) -> _Node | None:
        node = self._root
        depth = 0
        while node is not None:
            char = key[depth]
            if char < node.char:
                node = node.lo
            elif char > node.char:
                node = node.hi
            elif depth < len(key) - 1:
                node = node.eq
                depth += 1
            else:
                return node
        return None

    def __contains__(self, key: str) -> bool:
        if key == "":
            return False
        node = self._find(key)
        return node is not None and node.is_end

    def get(self, key: str, default: object = None) -> object:
        if key == "":
            return default
        node = self._find(key)
        return node.value if node is not None and node.is_end else default

    def keys(self) -> list:
        out: list = []
        _collect(self._root, "", out)
        return out

    def keys_with_prefix(self, prefix: str) -> list:
        out: list = []
        if prefix == "":
            _collect(self._root, "", out)
            return out
        node = self._find(prefix)
        if node is None:
            return out
        if node.is_end:
            out.append(prefix)
        _collect(node.eq, prefix, out)
        return out
