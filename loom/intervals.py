"""Intervals: an algebra of half-open integer ranges, merged and combined.

Tracking which parts of a document a pass touched, or which
character ranges a set of edits covers, is interval arithmetic,
and this provides it over half-open ranges, start inclusive and
end exclusive, the convention that makes adjacent ranges join
cleanly: zero-to-two and two-to-four are contiguous and merge
into zero-to-four, where a closed-end convention would leave a
one-unit argument about whether two belongs to both. Normalizing
is the core: it sorts the ranges, drops the empty ones where
start is not below end, and merges any that overlap or touch
into the fewest ranges that cover the same points, which is the
canonical form every other operation returns. Union is the
normalize of the two lists together; intersection walks both in
order taking the overlap of each pair; and difference walks the
first list subtracting the second, splitting a range around the
holes the subtrahend punches in it. Containment and total
length read off the normalized form, so they answer for the
coverage rather than the raw ranges, a point covered twice
counted once. The ranges are integers because the document
positions this serves are integers, and half-open because that
is the convention Python's own slicing uses, so a range here
and a slice there mean the same span without an off-by-one
translation between them.
"""

from __future__ import annotations

Interval = tuple[int, int]


def normalize(intervals: list[Interval]) -> list[Interval]:
    cleaned = sorted((start, end) for start, end in intervals if start < end)
    merged: list[Interval] = []
    for start, end in cleaned:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def total_length(intervals: list[Interval]) -> int:
    return sum(end - start for start, end in normalize(intervals))


def contains(intervals: list[Interval], point: int) -> bool:
    return any(start <= point < end for start, end in normalize(intervals))


def union(left: list[Interval], right: list[Interval]) -> list[Interval]:
    return normalize(left + right)


def intersection(
    left: list[Interval], right: list[Interval]
) -> list[Interval]:
    a = normalize(left)
    b = normalize(right)
    out: list[Interval] = []
    i = j = 0
    while i < len(a) and j < len(b):
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])
        if start < end:
            out.append((start, end))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def difference(
    left: list[Interval], right: list[Interval]
) -> list[Interval]:
    holes = normalize(right)
    out: list[Interval] = []
    for start, end in normalize(left):
        cursor = start
        for hole_start, hole_end in holes:
            if hole_end <= cursor or hole_start >= end:
                continue
            if hole_start > cursor:
                out.append((cursor, hole_start))
            cursor = max(cursor, hole_end)
            if cursor >= end:
                break
        if cursor < end:
            out.append((cursor, end))
    return out
