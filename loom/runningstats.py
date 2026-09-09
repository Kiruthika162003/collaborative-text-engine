"""Running stats: mean and variance updated one value at a time, and a moving average.

Some statistics must be computed over a stream too long to hold,
or updated as each value arrives, and this does that without
keeping the values. The running mean and variance use Welford's
method, which updates both from each new value in one pass using
only the count, the current mean, and a running sum of squared
deviations, so a million values are summarized in constant
space and the variance comes out without the catastrophic
cancellation that the naive mean-of-squares-minus-square-of-mean
formula suffers when the values are large and close together.
That numerical stability is the reason to use Welford's rather
than the textbook formula, and it is the reason this exists as
its own thing rather than deferring to summing the values. The
moving average is the other streaming need, the average of the
last few values rather than all of them, and it keeps a window
of that many, dropping the oldest as each new one arrives, so it
tracks a recent trend rather than the whole history, which is
what a smoothing over a noisy signal wants. The running variance
is the population variance, dividing by the count, stated the
same way the batch statistics module states it, so the two agree
on the same data. An empty accumulator reports zero for its mean
and variance rather than dividing by a zero count, the honest
floor for a summary of nothing, and the count is available so a
caller can tell a real zero mean from the empty one. Both are
accumulators a caller feeds and queries, holding no values a
caller could read back, because holding them would defeat the
constant space that is the point.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field


@dataclass
class RunningStats:
    count: int = 0
    _mean: float = 0.0
    _sum_sq: float = 0.0

    def add(self, value: float) -> None:
        self.count += 1
        delta = value - self._mean
        self._mean += delta / self.count
        self._sum_sq += delta * (value - self._mean)

    def mean(self) -> float:
        return self._mean if self.count else 0.0

    def variance(self) -> float:
        return self._sum_sq / self.count if self.count else 0.0

    def stddev(self) -> float:
        return math.sqrt(self.variance())


@dataclass
class MovingAverage:
    window: int
    _values: deque = field(default_factory=deque)

    def add(self, value: float) -> None:
        self._values.append(value)
        while len(self._values) > self.window:
            self._values.popleft()

    def average(self) -> float:
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)
