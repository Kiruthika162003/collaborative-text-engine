from __future__ import annotations

import random

from loom.dutchflag import partition


class TestPartition:
    def test_three_groups(self):
        arranged, low, high = partition([3, 1, 2, 5, 3, 0, 4], 3)
        assert all(value < 3 for value in arranged[:low])
        assert all(value == 3 for value in arranged[low:high])
        assert all(value > 3 for value in arranged[high:])

    def test_all_equal(self):
        arranged, low, high = partition([2, 2, 2], 2)
        assert (low, high) == (0, 3)
        assert arranged == [2, 2, 2]

    def test_all_less(self):
        _, low, high = partition([1, 0, 1], 5)
        assert low == 3
        assert high == 3

    def test_all_greater(self):
        _, low, high = partition([7, 8, 9], 5)
        assert low == 0
        assert high == 0

    def test_the_input_is_not_mutated(self):
        data = [3, 1, 2]
        partition(data, 2)
        assert data == [3, 1, 2]


class TestInvariant:
    def test_it_is_a_permutation_and_grouped(self):
        rng = random.Random(31)
        for _ in range(500):
            data = [rng.randint(0, 6) for _ in range(rng.randint(0, 30))]
            pivot = rng.randint(0, 6)
            arranged, low, high = partition(data, pivot)
            assert sorted(arranged) == sorted(data)
            assert all(value < pivot for value in arranged[:low])
            assert all(value == pivot for value in arranged[low:high])
            assert all(value > pivot for value in arranged[high:])
