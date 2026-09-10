"""Dutch flag: partition around a pivot into less, equal, and greater in a single in-place pass.

The Dutch national flag problem, named by Dijkstra for a flag of
three stripes, is to arrange a list into three groups, elements less
than a pivot, elements equal to it, and elements greater, all in one
pass. It is the partition step that a three-way quicksort needs, and
it is done with three pointers: one marking the end of the less-than
region growing from the front, one marking the start of the
greater-than region growing from the back, and one scanning the
unexamined middle. The scanner looks at each element and, if it is
less than the pivot, swaps it down to the less-than region and
advances both the boundary and the scanner; if greater, swaps it up
to the greater-than region and shrinks that boundary; if equal,
leaves it and advances only the scanner. When the scanner meets the
greater-than boundary the list is partitioned. The subtlety, and the
off-by-one I got wrong first, is the greater-than case: after
swapping an element up to the back, the scanner must not advance,
because the element that swap brought into the scanner's position
has not been examined yet, and advancing past it lets an unexamined
element slip into the finished region. I had assumed the scanner
should step forward after every swap the way the less-than case
does; it must not in the greater-than case, and a version that
advances unconditionally quietly misplaces elements. Only the
less-than swap advances the scanner, because there the element
swapped into place came from the already-scanned less region and is
known. The whole thing is one pass and touches each element a
bounded number of times, needs no extra lists, and this reports the
two boundaries so the equal region can be located, which is what
makes it a partition rather than merely a sort of three values.
"""

from __future__ import annotations


def partition(items: list, pivot: object) -> tuple[list, int, int]:
    arranged = list(items)
    low = 0
    scan = 0
    high = len(arranged)
    while scan < high:
        current = arranged[scan]
        if current < pivot:
            arranged[low], arranged[scan] = arranged[scan], arranged[low]
            low += 1
            scan += 1
        elif current > pivot:
            high -= 1
            arranged[scan], arranged[high] = arranged[high], arranged[scan]
        else:
            scan += 1
    return arranged, low, scan
