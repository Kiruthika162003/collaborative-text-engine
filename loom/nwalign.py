"""Needleman-Wunsch: line two sequences up end to end, scoring matches against gaps.

Global alignment answers a different question than edit distance,
though it fills a similar table: not how many operations separate
two sequences but how they best lay against each other over their
whole length, which character pairs with which and where gaps have
to open so the rest can line up. It scores an alignment by rewarding
a matched pair, penalizing a mismatched one, and penalizing a gap,
and it finds the alignment of highest total score by filling a grid
where each cell holds the best score for aligning the two prefixes
that reach it. Each cell is the best of three moves: pair the two
current characters, taking the diagonal cell's score plus the match
or mismatch reward; or open a gap in one sequence, taking a
neighbouring cell's score plus the gap penalty. The bottom-right
cell holds the best score for the whole pair, and walking back from
it, at each step undoing whichever move produced the cell, spells
out the alignment itself, the two sequences with gap characters
inserted so they read down in columns. I had assumed that once the
scoring was fixed the alignment was unique, that there was one best
way; there is one best score but often several alignments that
achieve it, because ties among the three moves are common, and
which one the traceback returns depends purely on which move it
prefers when scores tie. So the score is well defined and the
alignment shown is one representative among possibly many equally
good ones, which is the honest caveat: two tools with different tie
preferences can report different alignments of the same pair at the
same score, and comparing alignments therefore means fixing a
tie-break, which this does by preferring the diagonal, then the gap
in the first sequence, then the gap in the second. Dropping the gap
characters from either aligned sequence returns the original, which
is the invariant that says the alignment only inserted spacing and
changed nothing else.
"""

from __future__ import annotations

GAP = "-"


def align(
    first: str,
    second: str,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -1,
) -> tuple[str, str, int]:
    rows = len(first)
    cols = len(second)
    score = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(1, rows + 1):
        score[i][0] = i * gap
    for j in range(1, cols + 1):
        score[0][j] = j * gap
    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            reward = match if first[i - 1] == second[j - 1] else mismatch
            pairing = score[i - 1][j - 1] + reward
            drop_first = score[i - 1][j] + gap
            drop_second = score[i][j - 1] + gap
            score[i][j] = max(pairing, drop_first, drop_second)

    aligned_first: list[str] = []
    aligned_second: list[str] = []
    i, j = rows, cols
    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and score[i][j]
            == score[i - 1][j - 1] + (match if first[i - 1] == second[j - 1] else mismatch)
        ):
            aligned_first.append(first[i - 1])
            aligned_second.append(second[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and score[i][j] == score[i - 1][j] + gap:
            aligned_first.append(first[i - 1])
            aligned_second.append(GAP)
            i -= 1
        else:
            aligned_first.append(GAP)
            aligned_second.append(second[j - 1])
            j -= 1
    aligned_first.reverse()
    aligned_second.reverse()
    return "".join(aligned_first), "".join(aligned_second), score[rows][cols]


def score_of(first: str, second: str, match: int = 1, mismatch: int = -1, gap: int = -1) -> int:
    return align(first, second, match, mismatch, gap)[2]
