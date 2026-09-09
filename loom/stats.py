"""Stats: the common summary statistics over a list of numbers, computed plainly.

Several modules here compute a statistic for their own purpose;
this is the shared toolkit they could draw on, the summary
statistics a caller wants over any list of numbers. The mean is
the average, the median the middle value or the average of the
two middles for an even count, and the mode the most common
value with ties broken toward the smaller so the answer is
deterministic. The variance is the population variance, the
mean squared deviation about the mean, and the standard
deviation its square root, and the choice of population over
sample is stated because the two differ by a factor a caller
comparing against another tool needs to know: this divides by
the count, not the count minus one, which is right when the
data is the whole population and slightly low when it is a
sample of a larger one. The quantile interpolates linearly
between the order statistics, so the median is the fiftieth
quantile and a quarter point falls proportionally between the
two values it lies between, which is one of several quantile
conventions and named as the one chosen. Every function refuses
empty data rather than returning a zero that would pretend a
mean of nothing is a number, because the mean of no values is
undefined and a silent zero would poison an average of averages
downstream. The functions take plain lists so a caller composes
them with whatever produced the numbers, keeping the statistics
independent of where the data came from.
"""

from __future__ import annotations

import math
from collections import Counter

from loom.errors import Invalid


def _require(data: list[float]) -> None:
    if not data:
        raise Invalid("no data to summarize")


def mean(data: list[float]) -> float:
    _require(data)
    return sum(data) / len(data)


def median(data: list[float]) -> float:
    _require(data)
    ordered = sorted(data)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2


def mode(data: list[float]) -> float:
    _require(data)
    counts = Counter(data)
    best = max(counts.values())
    return min(value for value, count in counts.items() if count == best)


def variance(data: list[float]) -> float:
    _require(data)
    average = mean(data)
    return sum((value - average) ** 2 for value in data) / len(data)


def stddev(data: list[float]) -> float:
    return math.sqrt(variance(data))


def quantile(data: list[float], q: float) -> float:
    _require(data)
    if not 0 <= q <= 1:
        raise Invalid("a quantile is between zero and one")
    ordered = sorted(data)
    if len(ordered) == 1:
        return float(ordered[0])
    position = q * (len(ordered) - 1)
    low = int(position)
    fraction = position - low
    if low + 1 < len(ordered):
        return ordered[low] + (ordered[low + 1] - ordered[low]) * fraction
    return float(ordered[low])


def data_range(data: list[float]) -> float:
    _require(data)
    return max(data) - min(data)
