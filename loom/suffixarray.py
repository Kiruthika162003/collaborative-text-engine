"""Suffix array: the sorted order of a text's suffixes, and the overlaps between neighbours.

Many questions about a text are really questions about its
suffixes. Does a pattern occur? It occurs exactly when it is the
start of some suffix. How many times? As many suffixes as it
starts. What is the longest substring that appears twice? It is
the longest start shared by two suffixes. A suffix array answers
all of these by sorting the suffixes and storing not the suffixes
themselves but their starting positions in sorted order, so the
suffixes that begin with the same run land next to each other and
a pattern's occurrences become a contiguary block that a binary
search finds. The sort is the interesting part. Comparing suffixes
directly would compare long strings, so instead the positions are
sorted in rounds of doubling reach: first by their first
character, then by their first two, then four, then eight, each
round reusing the ranks from the last so a comparison looks at two
small numbers rather than a stretch of text, and the rounds needed
are the logarithm of the length. I had guessed sorting the
suffixes meant copying each one and sorting the copies, which
would be quadratic in space for a long text; it does not, the
array holds only the starting positions and the doubling compares
by rank, so the space stays linear in the length while the sort is
the length times the square of its logarithm. Alongside the order
sits the overlap between each pair of neighbours, the length of
the start they share, computed in one linear pass by the
observation that dropping the first character of a suffix shortens
its overlap with its neighbour by at most one, so the work never
restarts from zero. That overlap array is where the longest
repeated substring falls out for free: it is the tallest neighbour
overlap, because the two most similar suffixes in sorted order are
always adjacent, so the deepest agreement anywhere is the deepest
agreement between neighbours, which is the honest reason the
sorting was worth doing rather than scanning for repeats directly.
"""

from __future__ import annotations


def suffix_array(text: str) -> list[int]:
    length = len(text)
    if length == 0:
        return []
    order = list(range(length))
    rank = [ord(char) for char in text]
    step = 1
    while True:
        keys = [
            (rank[index], rank[index + step] if index + step < length else -1)
            for index in range(length)
        ]
        order.sort(key=lambda index, table=keys: table[index])
        fresh = [0] * length
        for position in range(1, length):
            same = keys[order[position]] == keys[order[position - 1]]
            fresh[order[position]] = fresh[order[position - 1]] + (0 if same else 1)
        rank = fresh
        if rank[order[-1]] == length - 1:
            break
        step *= 2
    return order


def lcp_array(text: str, order: list[int]) -> list[int]:
    length = len(text)
    if length == 0:
        return []
    rank = [0] * length
    for position, suffix in enumerate(order):
        rank[suffix] = position
    overlaps = [0] * length
    reach = 0
    for suffix in range(length):
        if rank[suffix] == 0:
            reach = 0
            continue
        neighbour = order[rank[suffix] - 1]
        while (
            suffix + reach < length
            and neighbour + reach < length
            and text[suffix + reach] == text[neighbour + reach]
        ):
            reach += 1
        overlaps[rank[suffix]] = reach
        if reach > 0:
            reach -= 1
    return overlaps


class SuffixArray:
    __slots__ = ("_lcp", "order", "text")

    def __init__(self, text: str) -> None:
        self.text = text
        self.order = suffix_array(text)
        self._lcp: list[int] | None = None

    def lcp(self) -> list[int]:
        if self._lcp is None:
            self._lcp = lcp_array(self.text, self.order)
        return self._lcp

    def _lower_bound(self, pattern: str) -> int:
        low, high = 0, len(self.order)
        span = len(pattern)
        while low < high:
            mid = (low + high) // 2
            start = self.order[mid]
            if self.text[start : start + span] < pattern:
                low = mid + 1
            else:
                high = mid
        return low

    def search(self, pattern: str) -> list[int]:
        if pattern == "":
            return sorted(range(len(self.text) + 1))
        start = self._lower_bound(pattern)
        span = len(pattern)
        found = []
        for position in range(start, len(self.order)):
            begin = self.order[position]
            if self.text[begin : begin + span] == pattern:
                found.append(begin)
            else:
                break
        return sorted(found)

    def contains(self, pattern: str) -> bool:
        return bool(self.search(pattern))

    def count(self, pattern: str) -> int:
        return len(self.search(pattern))

    def longest_repeated_substring(self) -> str:
        overlaps = self.lcp()
        if not overlaps:
            return ""
        best = max(range(len(overlaps)), key=lambda i: overlaps[i])
        length = overlaps[best]
        start = self.order[best]
        return self.text[start : start + length]
