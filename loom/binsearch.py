"""Binary search: the search and its bound variants over a sorted list.

Binary search halves a sorted list each step to find where a
value belongs in the length's logarithm rather than its size,
and the useful thing is not one function but the family of
bounds that share the halving. The left bound is the first
position at or after which the target could be inserted keeping
the list sorted, the index of the first element not less than
the target; the right bound is the first position strictly
after the target, the first element greater than it. Between
those two bounds sit exactly the elements equal to the target,
so their difference is how many times the target occurs, and
whether the left bound points at the target says whether it is
present at all. From those two the rest fall out: contains,
find returning an index or a not-found marker, and count.
Keeping the two bounds as the primitives and deriving the rest
is what makes the equal-elements cases correct, where a single
naive search returns some arbitrary one of several equal
elements and cannot tell how many there are. The one
precondition is that the list is sorted, stated plainly,
because binary search on unsorted data does not fail loudly, it
returns a confident wrong answer, so a caller passing unsorted
input has a bug the search cannot catch for them. The
comparisons use the elements' own ordering, so anything
sortable can be searched, and the bounds are half-open indices
into the list, the same convention slicing uses, so a bound is
directly a slice endpoint without an off-by-one.
"""

from __future__ import annotations


def bisect_left(data: list, target) -> int:
    low, high = 0, len(data)
    while low < high:
        mid = (low + high) // 2
        if data[mid] < target:
            low = mid + 1
        else:
            high = mid
    return low


def bisect_right(data: list, target) -> int:
    low, high = 0, len(data)
    while low < high:
        mid = (low + high) // 2
        if data[mid] <= target:
            low = mid + 1
        else:
            high = mid
    return low


def contains(data: list, target) -> bool:
    index = bisect_left(data, target)
    return index < len(data) and data[index] == target


def find(data: list, target) -> int:
    index = bisect_left(data, target)
    if index < len(data) and data[index] == target:
        return index
    return -1


def count(data: list, target) -> int:
    return bisect_right(data, target) - bisect_left(data, target)
