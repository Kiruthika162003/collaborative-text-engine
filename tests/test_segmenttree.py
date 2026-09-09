from __future__ import annotations

import random

import pytest

from loom.errors import Invalid
from loom.segmenttree import SegmentTree


class TestSum:
    def test_range_sums(self):
        tree = SegmentTree.for_sum([3, 1, 4, 1, 5, 9, 2, 6])
        assert tree.query(0, 8) == 31
        assert tree.query(2, 5) == 4 + 1 + 5
        assert tree.query(3, 3) == 0

    def test_update_changes_later_queries(self):
        tree = SegmentTree.for_sum([1, 2, 3, 4])
        tree.update(1, 20)
        assert tree.value(1) == 20
        assert tree.query(0, 4) == 1 + 20 + 3 + 4


class TestMinMax:
    def test_range_minimum(self):
        tree = SegmentTree.for_min([5, 2, 7, 1, 9, 3])
        assert tree.query(0, 6) == 1
        assert tree.query(0, 3) == 2
        assert tree.query(4, 6) == 3

    def test_range_maximum_after_update(self):
        tree = SegmentTree.for_max([5, 2, 7, 1, 9, 3])
        assert tree.query(0, 6) == 9
        tree.update(4, 0)
        assert tree.query(0, 6) == 7


class TestNonCommutative:
    def test_string_concatenation_keeps_order(self):
        tree = SegmentTree(list("collaborate"), lambda a, b: a + b, "")
        assert tree.query(0, 11) == "collaborate"
        assert tree.query(3, 7) == "labo"


class TestGuards:
    def test_an_out_of_range_update_is_refused(self):
        with pytest.raises(Invalid):
            SegmentTree.for_sum([1, 2]).update(2, 9)

    def test_an_out_of_range_query_is_refused(self):
        with pytest.raises(Invalid):
            SegmentTree.for_sum([1, 2]).query(0, 3)


class TestAgainstNaive:
    def test_min_matches_a_plain_list_over_random_ops(self):
        rng = random.Random(42)
        size = 50
        shadow = [rng.randint(0, 100) for _ in range(size)]
        tree = SegmentTree.for_min(shadow)
        for _ in range(1000):
            if rng.random() < 0.5:
                index = rng.randrange(size)
                value = rng.randint(0, 100)
                tree.update(index, value)
                shadow[index] = value
            low = rng.randrange(size)
            high = rng.randint(low + 1, size)
            assert tree.query(low, high) == min(shadow[low:high])
