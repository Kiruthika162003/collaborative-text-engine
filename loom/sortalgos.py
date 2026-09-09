"""Sort algos: the classic sorting algorithms, written out for their own sake.

Sorting is solved, and a caller wanting a sorted list uses the
built-in; these are the textbook algorithms written explicitly,
which an engine about structure benefits from having plainly
rather than only as a library call, and which differ in ways
worth being able to point at. Insertion sort builds the result
one element at a time, sliding each new element back to its
place, which is quadratic in general but genuinely fast on
nearly-sorted input where each element moves little, the case
where it beats the fancier ones. Merge sort splits the list in
half, sorts each half, and merges the two sorted halves, which
is a guaranteed n-log-n and stable, keeping equal elements in
their original order, at the cost of the extra space the merge
needs. Quicksort partitions around a pivot into the smaller, the
equal, and the larger, and sorts the outer parts, which is fast
in practice and in place in its usual form, though this
three-way version returns new lists for clarity at the cost of
that in-place property. All three return a new sorted list and
leave the input untouched, and all sort by the elements' own
comparison, so anything sortable sorts. They are named as
educational: the built-in sort is faster than any of these and
is what production code should use, and these exist to show how
the sorting is done and to be checked against a known result,
not to be reached for when a list simply needs ordering. Seeing
them side by side is the point, the same result reached three
ways with three different trade-offs of speed, stability, and
space that a caller choosing a sort in a lower-level language
would actually weigh.
"""

from __future__ import annotations


def insertion_sort(data: list) -> list:
    result = list(data)
    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    return result


def _merge(left: list, right: list) -> list:
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def merge_sort(data: list) -> list:
    if len(data) <= 1:
        return list(data)
    middle = len(data) // 2
    return _merge(merge_sort(data[:middle]), merge_sort(data[middle:]))


def quicksort(data: list) -> list:
    if len(data) <= 1:
        return list(data)
    pivot = data[len(data) // 2]
    less = [item for item in data if item < pivot]
    equal = [item for item in data if item == pivot]
    greater = [item for item in data if item > pivot]
    return quicksort(less) + equal + quicksort(greater)
