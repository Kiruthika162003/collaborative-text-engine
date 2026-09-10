"""Kadane: the largest sum of any contiguous stretch, found in a single forward pass.

Given a list of numbers, some positive and some negative, the
maximum subarray problem asks for the contiguous stretch whose sum
is largest. Checking every stretch is quadratic, a start and an end
for each, but Kadane's algorithm gets it in one pass with a single
running idea: keep the best sum of any stretch that ends exactly at
the current position, and update it by asking whether extending the
previous best-ending-here by the current number beats starting fresh
at the current number. Whenever the running sum so far has gone
negative, it can only drag down whatever follows, so the best stretch
ending at the next position abandons it and starts anew; whenever it
is positive, carrying it forward helps. The overall answer is the
largest of these best-ending-here values seen along the way. I had
guessed the greedy running sum could be fooled by a dip, that a
promising stretch interrupted by a run of negatives would be
wrongly cut off before a later recovery; it is not, because the
algorithm never discards the global best it has already recorded, it
only decides whether the stretch ending right here should keep its
past or drop it, and dropping a past that has gone negative is
always right since a negative prefix cannot improve any stretch
built on top of it. That is why one pass suffices and no
backtracking is needed. The all-negative case is the one that
catches a careless version: if every number is negative there is no
positive stretch, and a version that started its best at zero would
wrongly report zero as if the empty stretch were allowed, so this
starts from the first element and requires a non-empty stretch,
returning the least negative single element when that is the best
there is. It reports the sum together with the start and end
positions of a stretch that achieves it, so the answer can be
located and not merely scored.
"""

from __future__ import annotations

from loom.errors import Invalid


def maximum_subarray(numbers: list) -> tuple[object, int, int]:
    if not numbers:
        raise Invalid("the maximum subarray of an empty list is undefined")
    best_sum = numbers[0]
    best_start = 0
    best_end = 0
    current_sum = numbers[0]
    current_start = 0
    for index in range(1, len(numbers)):
        value = numbers[index]
        if current_sum < 0:
            current_sum = value
            current_start = index
        else:
            current_sum += value
        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index
    return best_sum, best_start, best_end


def maximum_sum(numbers: list) -> object:
    return maximum_subarray(numbers)[0]
