"""LIS: the longest strictly increasing subsequence, via the smallest tail per length.

Given a sequence, the longest increasing subsequence is the
longest set of positions, in order, whose values strictly climb,
and it is not a run of adjacent elements but a selection scattered
through the sequence. The patience method finds it without
comparing every pair. It scans the sequence once keeping an array
whose entry at each length is the smallest value that can end an
increasing subsequence of that length so far; each new value
either extends the array, when it is larger than every tail and so
begins a longer subsequence than any yet seen, or it replaces the
first tail that is not smaller than it, lowering that length's
ending value to keep the most room for future growth. The length
of that tails array at the end is the length of the answer,
because it grew by one exactly each time a longer subsequence
became possible, and the replacement, found by binary search since
the tails stay sorted, is what makes each step logarithmic and the
whole scan the length times the logarithm rather than the square.
I had guessed finding the longest increasing run meant comparing
every element against every earlier one, the quadratic table; it
does not, the smallest-tail-per-length trick gets the length in n
log n, which surprised me for a problem that looks inherently
pairwise. The trap I fell into first was reading the answer off the
tails array itself: its values are the right length but they are
not a real subsequence of the input, because later replacements can
overwrite a tail with a value that comes earlier in the sequence
than the ones after it, so the tails array is a length, not a path.
The actual subsequence has to be recovered separately, by
remembering for each element which element preceded it in the
subsequence that ended there, then walking those predecessors back
from the end, which is what this does to return a genuine
increasing subsequence rather than only its length.
"""

from __future__ import annotations

from bisect import bisect_left


def longest_increasing_subsequence(sequence: list) -> list:
    tails: list = []
    tail_index: list[int] = []
    predecessor = [-1] * len(sequence)
    for position, value in enumerate(sequence):
        slot = bisect_left(tails, value)
        if slot == len(tails):
            tails.append(value)
            tail_index.append(position)
        else:
            tails[slot] = value
            tail_index[slot] = position
        predecessor[position] = tail_index[slot - 1] if slot > 0 else -1
    if not tail_index:
        return []
    result = []
    cursor = tail_index[-1]
    while cursor != -1:
        result.append(sequence[cursor])
        cursor = predecessor[cursor]
    result.reverse()
    return result


def lis_length(sequence: list) -> int:
    tails: list = []
    for value in sequence:
        slot = bisect_left(tails, value)
        if slot == len(tails):
            tails.append(value)
        else:
            tails[slot] = value
    return len(tails)
