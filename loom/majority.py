"""Majority: the element that holds more than half, by one counter and a confirming pass.

If some element of a list appears more than half the time, the
Boyer-Moore voting algorithm finds it in a single pass using one
candidate and one counter, no tally of all the elements. It reads
along holding a candidate and a count: when the count is zero it
adopts the current element as the candidate with count one, when the
current element equals the candidate it raises the count, and when
it differs it lowers the count, as if the two elements paired off and
cancelled. A true majority element, one appearing more than half the
time, cannot be fully cancelled by all the others combined, because
there are not enough others to pair with every one of it, so it is
the candidate left standing at the end. I had guessed finding the
majority needed counting every element, a full frequency tally; the
voting pass finds the only possible majority with a single counter,
which surprised me for how little it remembers. The honest catch is
that the pass alone cannot confirm a majority exists: run it on a
list with no majority and it still leaves some candidate standing,
an arbitrary survivor of the cancellations, not a real majority. So
the candidate has to be verified by a second pass that counts its
actual occurrences and checks they exceed half, and a version that
trusts the first pass and skips the check returns that arbitrary
survivor as if it were a majority, confidently wrong whenever no
majority is present. This does the verification and reports honestly
that there is no strict majority rather than returning the phantom
the first pass leaves behind.
"""

from __future__ import annotations

from loom.errors import Invalid


def _candidate(items: list) -> object:
    candidate = None
    count = 0
    for item in items:
        if count == 0:
            candidate = item
            count = 1
        elif item == candidate:
            count += 1
        else:
            count -= 1
    return candidate


def majority(items: list) -> object:
    if not items:
        raise Invalid("an empty list has no majority")
    candidate = _candidate(items)
    if items.count(candidate) * 2 <= len(items):
        raise Invalid("no element holds a strict majority")
    return candidate


def majority_or_none(items: list) -> object:
    if not items:
        return None
    candidate = _candidate(items)
    return candidate if items.count(candidate) * 2 > len(items) else None
