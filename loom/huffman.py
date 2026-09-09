"""Huffman coding: spend short codes on common symbols and long ones on rare, provably least.

A fixed-width code gives every symbol the same number of bits
regardless of how often it appears, which wastes space whenever
some symbols are far more common than others, as the letters of
ordinary text are. Huffman coding gives the common symbols short
codes and the rare ones long codes, and does it in the way that
makes the total shortest. It builds a tree from the bottom: start
with one leaf per symbol weighted by how often the symbol occurs,
then repeatedly take the two lightest nodes and join them under a
new parent whose weight is their sum, until one tree remains. The
path from the root to a symbol's leaf, reading a zero for a left
step and a one for a right, is that symbol's code, and because the
lightest nodes were joined last they sit nearest the root with the
shortest paths, while the heaviest were joined first and sit
deepest, which is exactly the short-code-for-common arrangement.
The codes are prefix-free, no code is a prefix of another, because
every symbol is a leaf and a path to a leaf never passes through
another leaf, so a stream of them decodes without any separator:
read bits until they spell a code, emit that symbol, and start
over. I had guessed that on ordinary text a plain fixed-width code
and this would come out close, that the cleverness was mostly
theory; on text with the skewed letter frequencies real language
has, Huffman is materially shorter, and the size of the gap is the
size of the skew, so it pays off precisely when the data is uneven
and gives back almost nothing when the data is flat, which is the
honest boundary of when to reach for it. The building uses a heap
to keep pulling the two lightest, and ties are broken by a running
order number so the same input always builds the same tree, since
a code that depended on dictionary iteration order would decode on
one machine and not another. A single distinct symbol is the one
degenerate case, having no left or right to distinguish, and is
given the code zero by convention so that even a run of one letter
still encodes and decodes.
"""

from __future__ import annotations

import heapq
from collections import Counter

from loom.errors import Invalid


class _Branch:
    __slots__ = ("left", "right")

    def __init__(self, left: object, right: object) -> None:
        self.left = left
        self.right = right


class Huffman:
    __slots__ = ("_inverse", "table")

    def __init__(self, table: dict) -> None:
        self.table = table
        self._inverse = {code: symbol for symbol, code in table.items()}

    @classmethod
    def from_data(cls, data: str) -> Huffman:
        if data == "":
            raise Invalid("cannot build a code from no data")
        counts = Counter(data)
        if len(counts) == 1:
            (symbol,) = counts
            return cls({symbol: "0"})
        heap = [
            (count, order, symbol)
            for order, (symbol, count) in enumerate(sorted(counts.items()))
        ]
        heapq.heapify(heap)
        order = len(heap)
        while len(heap) > 1:
            weight_a, _, node_a = heapq.heappop(heap)
            weight_b, _, node_b = heapq.heappop(heap)
            heapq.heappush(heap, (weight_a + weight_b, order, _Branch(node_a, node_b)))
            order += 1
        _, _, root = heap[0]
        table: dict = {}
        _assign(root, "", table)
        return cls(table)

    def encode(self, data: str) -> str:
        try:
            return "".join(self.table[symbol] for symbol in data)
        except KeyError as missing:
            raise Invalid(f"symbol {missing} has no code in this table") from None

    def decode(self, bits: str) -> str:
        out = []
        buffer = ""
        for bit in bits:
            buffer += bit
            symbol = self._inverse.get(buffer)
            if symbol is not None:
                out.append(symbol)
                buffer = ""
        if buffer:
            raise Invalid("the trailing bits do not complete a symbol")
        return "".join(out)

    def encoded_length(self, data: str) -> int:
        return len(self.encode(data))


def _assign(node: object, prefix: str, table: dict) -> None:
    if isinstance(node, _Branch):
        _assign(node.left, prefix + "0", table)
        _assign(node.right, prefix + "1", table)
    else:
        table[node] = prefix
