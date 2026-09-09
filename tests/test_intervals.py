from __future__ import annotations

from loom.intervals import (
    contains,
    difference,
    intersection,
    normalize,
    total_length,
    union,
)


class TestNormalize:
    def test_overlapping_ranges_merge(self):
        assert normalize([(1, 3), (2, 5), (7, 8)]) == [(1, 5), (7, 8)]

    def test_adjacent_ranges_merge(self):
        assert normalize([(0, 2), (2, 4)]) == [(0, 4)]

    def test_empty_ranges_are_dropped(self):
        assert normalize([(3, 3), (1, 2)]) == [(1, 2)]


class TestMeasures:
    def test_total_length_counts_coverage_once(self):
        assert total_length([(0, 5), (3, 8)]) == 8

    def test_contains_checks_the_point(self):
        assert contains([(0, 5)], 4)
        assert not contains([(0, 5)], 5)


class TestSetOps:
    def test_union_merges_both(self):
        assert union([(0, 2)], [(1, 4)]) == [(0, 4)]

    def test_intersection_takes_the_overlap(self):
        assert intersection([(0, 5)], [(3, 8)]) == [(3, 5)]

    def test_disjoint_ranges_do_not_intersect(self):
        assert intersection([(0, 2)], [(5, 8)]) == []

    def test_difference_punches_holes(self):
        assert difference([(0, 10)], [(2, 4), (6, 8)]) == [
            (0, 2),
            (4, 6),
            (8, 10),
        ]

    def test_subtracting_everything_leaves_nothing(self):
        assert difference([(0, 5)], [(0, 5)]) == []
