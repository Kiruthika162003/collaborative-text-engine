"""LCS diff: diff two sequences from a longest-common-subsequence table by hand.

The line-diff module leans on the standard library's matcher;
this computes the same kind of diff from first principles, a
longest-common-subsequence table filled by dynamic programming
and then walked back to read off the edits. It is here for two
reasons: it works on any sequence of comparable items, not just
lines of a string, so a caller can diff lists of words or
tokens or records, and it makes the algorithm explicit and
testable rather than delegated, which matters in an engine
whose whole subject is reconciling changes. The table holds, at
each pair of positions, the length of the longest subsequence
common to the two tails, filled from the far corner inward, and
the backtrack starts at the front and at each step keeps a
matched item, or drops from whichever side the table says loses
nothing, which is what makes the diff minimal in edits. The
result is the space-minus-plus stream a reader knows, a kept
item, a removed one, an added one, and it reduces to the line
form through a convenience that splits and rejoins on newlines,
so a caller wanting a line diff has it and a caller wanting a
token diff has the same machinery. The cost is quadratic in the
lengths, the price of the exact table, which is fine for the
sentences and short lists it is meant for and, like the common-
substring module, stated as not the tool for enormous inputs
where a smarter diff pays its keep.
"""

from __future__ import annotations

from typing import TypeVar

Item = TypeVar("Item")


def diff(before: list[Item], after: list[Item]) -> list[tuple[str, Item]]:
    rows = len(before)
    cols = len(after)
    table = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if before[i] == after[j]:
                table[i][j] = table[i + 1][j + 1] + 1
            else:
                table[i][j] = max(table[i + 1][j], table[i][j + 1])
    result: list[tuple[str, Item]] = []
    i = j = 0
    while i < rows and j < cols:
        if before[i] == after[j]:
            result.append((" ", before[i]))
            i += 1
            j += 1
        elif table[i + 1][j] >= table[i][j + 1]:
            result.append(("-", before[i]))
            i += 1
        else:
            result.append(("+", after[j]))
            j += 1
    while i < rows:
        result.append(("-", before[i]))
        i += 1
    while j < cols:
        result.append(("+", after[j]))
        j += 1
    return result


def diff_lines(before: str, after: str) -> list[tuple[str, str]]:
    return diff(before.split("\n"), after.split("\n"))


def render(before: str, after: str) -> str:
    return "\n".join(
        f"{mark}{line}" for mark, line in diff_lines(before, after)
    )
