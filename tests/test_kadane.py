from __future__ import annotations

import random

import pytest

from loom.errors import Invalid
from loom.kadane import maximum_subarray, maximum_sum


def _brute_force(numbers: list) -> int:
    best = numbers[0]
    for start in range(len(numbers)):
        running = 0
        for end in range(start, len(numbers)):
            running += numbers[end]
            best = max(best, running)
    return best


class TestSum:
    def test_the_classic_example(self):
        numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        assert maximum_sum(numbers) == 6

    def test_all_positive_takes_everything(self):
        assert maximum_sum([1, 2, 3, 4]) == 10

    def test_all_negative_takes_the_least_bad(self):
        assert maximum_sum([-5, -2, -8, -1]) == -1

    def test_a_single_element(self):
        assert maximum_sum([7]) == 7

    def test_the_empty_list_is_refused(self):
        with pytest.raises(Invalid):
            maximum_subarray([])


class TestIndices:
    def test_it_returns_the_stretch(self):
        numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        total, start, end = maximum_subarray(numbers)
        assert total == 6
        assert numbers[start : end + 1] == [4, -1, 2, 1]
        assert sum(numbers[start : end + 1]) == total


class TestAgainstBruteForce:
    def test_matches_the_quadratic_scan(self):
        rng = random.Random(23)
        for _ in range(500):
            numbers = [rng.randint(-10, 10) for _ in range(rng.randint(1, 30))]
            total, start, end = maximum_subarray(numbers)
            assert total == _brute_force(numbers)
            assert sum(numbers[start : end + 1]) == total
