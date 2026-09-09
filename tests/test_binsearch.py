from __future__ import annotations

from loom.binsearch import bisect_left, bisect_right, contains, count, find


class TestBounds:
    def test_left_bound_finds_the_first_position(self):
        assert bisect_left([1, 3, 5], 3) == 1
        assert bisect_left([1, 3, 5], 4) == 2
        assert bisect_left([1, 3, 5], 0) == 0
        assert bisect_left([1, 3, 5], 9) == 3

    def test_right_bound_is_past_equal_elements(self):
        assert bisect_right([1, 3, 3, 5], 3) == 3

    def test_bounds_bracket_equal_elements(self):
        data = [1, 2, 2, 2, 3]
        assert bisect_left(data, 2) == 1
        assert bisect_right(data, 2) == 4


class TestDerived:
    def test_contains(self):
        assert contains([1, 3, 5], 3)
        assert not contains([1, 3, 5], 4)

    def test_find_returns_an_index_or_minus_one(self):
        assert find([1, 3, 5], 5) == 2
        assert find([1, 3, 5], 4) == -1

    def test_count_of_equal_elements(self):
        assert count([1, 2, 2, 2, 3], 2) == 3
        assert count([1, 2, 3], 9) == 0


class TestEmpty:
    def test_an_empty_list(self):
        assert bisect_left([], 1) == 0
        assert not contains([], 1)
