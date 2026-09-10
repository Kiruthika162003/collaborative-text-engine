"""Quickselect: the kth smallest element without sorting, by partitioning toward the rank.

Finding the kth smallest element of a list, the smallest, the
median, the ninetieth percentile, looks like it needs the list
sorted first so the answer can be read off by position, which costs
the length times its logarithm. Quickselect gets the one element
without paying for the full order. It borrows quicksort's
partition: pick a pivot, and rearrange the list so everything
smaller sits left of the pivot and everything larger sits right,
which lands the pivot at its final sorted position and tells you,
for free, what rank the pivot holds. If that rank is the one wanted,
the answer is the pivot; if the wanted rank is smaller, it must lie
in the left part and the right part can be ignored entirely; if
larger, only the right part matters. So unlike quicksort, which
recurses into both sides to order everything, quickselect recurses
into only the one side that can contain the rank, and each step
throws away a portion of the list. On average the discarded portion
is a constant fraction, so the work forms a shrinking geometric sum
that adds up to linear, less than a full sort by the logarithm
factor. I had guessed getting the kth element meant sorting first;
it does not when only one order statistic is wanted, and the saving
is real. The honest catch is the pivot: an unlucky choice that
always splits off just one element degrades it to quadratic, the
same worst case quicksort has, and the defence is the same, choose
the pivot at random so no particular input can reliably trigger the
bad splits, which makes the cost expected-linear rather than
guaranteed-linear. The pivot source is seedable here so the same
call gives the same internal choices and the behaviour is
reproducible, and the list handed in is copied rather than
reordered in place, since a query for one element should not
scramble the caller's data as a side effect.
"""

from __future__ import annotations

import random

from loom.errors import Invalid


def _partition(items: list, low: int, high: int, pivot_index: int) -> int:
    pivot = items[pivot_index]
    items[pivot_index], items[high] = items[high], items[pivot_index]
    store = low
    for scan in range(low, high):
        if items[scan] < pivot:
            items[store], items[scan] = items[scan], items[store]
            store += 1
    items[store], items[high] = items[high], items[store]
    return store


def quickselect(data: list, k: int, seed: int | None = None) -> object:
    if not 0 <= k < len(data):
        raise Invalid(f"rank {k} out of range 0..{len(data) - 1}")
    items = list(data)
    rng = random.Random(seed)
    low, high = 0, len(items) - 1
    while low != high:
        pivot_index = rng.randint(low, high)
        pivot_index = _partition(items, low, high, pivot_index)
        if k == pivot_index:
            return items[k]
        if k < pivot_index:
            high = pivot_index - 1
        else:
            low = pivot_index + 1
    return items[low]


def median(data: list, seed: int | None = None) -> object:
    count = len(data)
    if count == 0:
        raise Invalid("the median of no data is undefined")
    if count % 2 == 1:
        return quickselect(data, count // 2, seed)
    lower = quickselect(data, count // 2 - 1, seed)
    upper = quickselect(data, count // 2, seed)
    return (lower + upper) / 2
