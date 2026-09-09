from __future__ import annotations

import pytest

from loom.sortalgos import insertion_sort, merge_sort, quicksort

ALGORITHMS = [insertion_sort, merge_sort, quicksort]


class TestSorting:
    @pytest.mark.parametrize("sort", ALGORITHMS)
    def test_it_sorts(self, sort):
        assert sort([5, 3, 8, 1, 9, 2]) == [1, 2, 3, 5, 8, 9]

    @pytest.mark.parametrize("sort", ALGORITHMS)
    def test_duplicates(self, sort):
        assert sort([2, 1, 2, 1, 3]) == [1, 1, 2, 2, 3]

    @pytest.mark.parametrize("sort", ALGORITHMS)
    def test_empty_and_single(self, sort):
        assert sort([]) == []
        assert sort([7]) == [7]

    @pytest.mark.parametrize("sort", ALGORITHMS)
    def test_strings(self, sort):
        assert sort(["cherry", "apple", "banana"]) == [
            "apple",
            "banana",
            "cherry",
        ]

    @pytest.mark.parametrize("sort", ALGORITHMS)
    def test_the_input_is_not_mutated(self, sort):
        data = [3, 1, 2]
        sort(data)
        assert data == [3, 1, 2]


class TestStability:
    def test_merge_sort_is_stable(self):
        pairs = [(1, "a"), (2, "b"), (1, "c"), (2, "d")]
        result = merge_sort(pairs)
        assert result == [(1, "a"), (1, "c"), (2, "b"), (2, "d")]
