from __future__ import annotations

from loom.orderedset import of


class TestOrder:
    def test_insertion_order_is_kept_and_deduplicated(self):
        assert of([3, 1, 2, 1, 3]).items() == [3, 1, 2]

    def test_re_adding_keeps_the_first_position(self):
        ordered = of([1, 2])
        ordered.add(1)
        assert ordered.items() == [1, 2]

    def test_discard_removes(self):
        ordered = of([1, 2, 3])
        ordered.discard(2)
        assert ordered.items() == [1, 3]


class TestSetOps:
    def test_union_is_left_anchored(self):
        assert of([3, 1]).union(of([1, 2])).items() == [3, 1, 2]

    def test_intersection_keeps_left_order(self):
        assert of([3, 2, 1]).intersection(of([1, 2])).items() == [2, 1]

    def test_difference(self):
        assert of([1, 2, 3]).difference(of([2])).items() == [1, 3]


class TestAccess:
    def test_membership_and_length(self):
        ordered = of([1, 2, 3])
        assert 2 in ordered
        assert 9 not in ordered
        assert len(ordered) == 3

    def test_iteration_is_ordered(self):
        assert list(of([3, 1, 2])) == [3, 1, 2]
