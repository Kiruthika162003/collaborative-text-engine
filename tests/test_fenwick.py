from __future__ import annotations

import random

import pytest

from loom.errors import Invalid
from loom.fenwick import Fenwick


class TestPrefixSums:
    def test_prefix_sums_of_a_known_sequence(self):
        tree = Fenwick.from_values([3, 1, 4, 1, 5, 9, 2, 6])
        assert tree.prefix_sum(0) == 0
        assert tree.prefix_sum(1) == 3
        assert tree.prefix_sum(4) == 9
        assert tree.prefix_sum(8) == 31

    def test_range_sum(self):
        tree = Fenwick.from_values([3, 1, 4, 1, 5, 9, 2, 6])
        assert tree.range_sum(2, 5) == 4 + 1 + 5
        assert tree.range_sum(0, 8) == 31
        assert tree.range_sum(3, 3) == 0

    def test_single_values_read_back(self):
        values = [3, 1, 4, 1, 5, 9, 2, 6]
        tree = Fenwick.from_values(values)
        for index, value in enumerate(values):
            assert tree.value(index) == value


class TestUpdates:
    def test_add_updates_later_prefixes(self):
        tree = Fenwick.from_values([1, 2, 3, 4])
        tree.add(1, 10)
        assert tree.value(1) == 12
        assert tree.prefix_sum(4) == 20

    def test_set_replaces_a_value(self):
        tree = Fenwick.from_values([1, 2, 3, 4])
        tree.set(2, 30)
        assert tree.value(2) == 30
        assert tree.prefix_sum(4) == 1 + 2 + 30 + 4


class TestGuards:
    def test_an_out_of_range_index_is_refused(self):
        with pytest.raises(Invalid):
            Fenwick(4).add(4, 1)

    def test_an_out_of_range_prefix_is_refused(self):
        with pytest.raises(Invalid):
            Fenwick(4).prefix_sum(5)


class TestAgainstNaive:
    def test_matches_a_plain_list_over_random_ops(self):
        rng = random.Random(7)
        size = 64
        shadow = [0] * size
        tree = Fenwick(size)
        for _ in range(1000):
            index = rng.randrange(size)
            delta = rng.randint(-5, 5)
            tree.add(index, delta)
            shadow[index] += delta
            low = rng.randrange(size)
            high = rng.randint(low, size)
            assert tree.range_sum(low, high) == sum(shadow[low:high])
