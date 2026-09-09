"""Common substrings: the longest shared run and the longest shared subsequence.

Two texts often share a passage, and there are two senses of
shared worth computing. The longest common substring is the
longest run of characters that appears contiguously in both,
which finds a quoted sentence or a pasted paragraph, and the
longest common subsequence is the longest sequence of
characters that appears in both in order but not necessarily
together, which is what a diff is built on and measures how
much of one text survives into the other. Both are the
classic dynamic-programming computations, a table over the two
strings filled in one pass, the substring tracking the best
contiguous match and the subsequence building the shared
sequence as it goes. Where several matches tie for longest,
this returns one of them rather than all, and which one is a
consequence of the fill order rather than a promise, so a
caller who needs every maximal match needs more than the
longest; that is named because a caller comparing the result
against a hand-picked expectation should know the tie-break is
incidental. The computations are quadratic in the input
lengths, fine for the sentences and paragraphs this compares
and not meant for whole books, which is stated so a caller
does not reach for it at a scale where a suffix-automaton
approach is the right tool and this is the wrong one.
"""

from __future__ import annotations


def longest_common_substring(first: str, second: str) -> str:
    if not first or not second:
        return ""
    table = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
    best = 0
    end = 0
    for i in range(1, len(first) + 1):
        for j in range(1, len(second) + 1):
            if first[i - 1] == second[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
                if table[i][j] > best:
                    best = table[i][j]
                    end = i
    return first[end - best : end]


def longest_common_subsequence(first: str, second: str) -> str:
    table = [[""] * (len(second) + 1) for _ in range(len(first) + 1)]
    for i in range(1, len(first) + 1):
        for j in range(1, len(second) + 1):
            if first[i - 1] == second[j - 1]:
                table[i][j] = table[i - 1][j - 1] + first[i - 1]
            else:
                table[i][j] = max(
                    table[i - 1][j], table[i][j - 1], key=len
                )
    return table[len(first)][len(second)]


def lcs_length(first: str, second: str) -> int:
    return len(longest_common_subsequence(first, second))
