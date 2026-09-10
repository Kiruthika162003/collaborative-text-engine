from __future__ import annotations

import random
import statistics

import pytest

from loom.errors import Invalid
from loom.quickselect import median, quickselect


class TestSelect:
    def test_the_smallest_and_largest(self):
        data = [5, 3, 8, 1, 9, 2]
        assert quickselect(data, 0) == 1
        assert quickselect(data, len(data) - 1) == 9

    def test_a_middle_rank(self):
        data = [5, 3, 8, 1, 9, 2]
        assert quickselect(data, 2) == 3

    def test_the_input_is_not_mutated(self):
        data = [3, 1, 2]
        quickselect(data, 1)
        assert data == [3, 1, 2]

    def test_an_out_of_range_rank_is_refused(self):
        with pytest.raises(Invalid):
            quickselect([1, 2, 3], 5)


class TestAgainstSorted:
    def test_matches_sorted_indexing_over_random_inputs(self):
        rng = random.Random(7)
        for _ in range(200):
            size = rng.randint(1, 40)
            data = [rng.randint(-20, 20) for _ in range(size)]
            k = rng.randrange(size)
            assert quickselect(data, k, seed=1) == sorted(data)[k]

    def test_duplicates_are_handled(self):
        data = [4, 4, 4, 1, 4, 4]
        assert quickselect(data, 0) == 1
        assert quickselect(data, 1) == 4


class TestMedian:
    def test_odd_length(self):
        assert median([5, 3, 1, 2, 4]) == 3

    def test_even_length(self):
        assert median([1, 2, 3, 4]) == 2.5

    def test_matches_the_statistics_module(self):
        rng = random.Random(11)
        for _ in range(100):
            data = [rng.randint(0, 50) for _ in range(rng.randint(1, 30))]
            assert median(data, seed=2) == statistics.median(data)

    def test_the_median_of_nothing_is_refused(self):
        with pytest.raises(Invalid):
            median([])
