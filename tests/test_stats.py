from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.stats import (
    data_range,
    mean,
    median,
    mode,
    quantile,
    stddev,
    variance,
)


class TestCentral:
    def test_mean(self):
        assert mean([1, 2, 3, 4]) == 2.5

    def test_median_odd(self):
        assert median([3, 1, 2]) == 2

    def test_median_even(self):
        assert median([1, 2, 3, 4]) == 2.5

    def test_mode_breaks_ties_low(self):
        assert mode([1, 1, 2, 2, 3]) == 1


class TestSpread:
    def test_population_variance(self):
        assert variance([1, 2, 3]) == pytest.approx(2 / 3)

    def test_stddev(self):
        assert stddev([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2.0)

    def test_range(self):
        assert data_range([3, 7, 1]) == 6


class TestQuantile:
    def test_the_median_quantile(self):
        assert quantile([1, 2, 3, 4], 0.5) == 2.5

    def test_the_extremes(self):
        assert quantile([1, 2, 3, 4], 0) == 1
        assert quantile([1, 2, 3, 4], 1) == 4

    def test_interpolation(self):
        assert quantile([1, 2, 3, 4], 0.25) == 1.75

    def test_a_bad_q_is_refused(self):
        with pytest.raises(Invalid):
            quantile([1, 2], 2)


class TestGuards:
    def test_empty_data_is_refused(self):
        with pytest.raises(Invalid):
            mean([])
