from __future__ import annotations

import pytest

from loom.runningstats import MovingAverage, RunningStats


class TestRunningStats:
    def test_mean_and_variance(self):
        stats = RunningStats()
        for value in [1, 2, 3, 4]:
            stats.add(value)
        assert stats.mean() == 2.5
        assert stats.variance() == pytest.approx(1.25)

    def test_stddev(self):
        stats = RunningStats()
        for value in [2, 4, 4, 4, 5, 5, 7, 9]:
            stats.add(value)
        assert stats.stddev() == pytest.approx(2.0)

    def test_an_empty_accumulator_is_zero(self):
        stats = RunningStats()
        assert stats.mean() == 0.0
        assert stats.variance() == 0.0

    def test_stability_with_large_close_values(self):
        stats = RunningStats()
        for value in [1_000_000_001, 1_000_000_002, 1_000_000_003]:
            stats.add(value)
        assert stats.variance() == pytest.approx(2 / 3)


class TestMovingAverage:
    def test_it_averages_the_window(self):
        avg = MovingAverage(3)
        for value in [1, 2, 3, 4]:
            avg.add(value)
        assert avg.average() == 3.0

    def test_before_the_window_fills(self):
        avg = MovingAverage(3)
        avg.add(2)
        avg.add(4)
        assert avg.average() == 3.0

    def test_an_empty_moving_average_is_zero(self):
        assert MovingAverage(3).average() == 0.0
