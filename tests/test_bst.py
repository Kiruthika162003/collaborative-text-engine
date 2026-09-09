from __future__ import annotations

import pytest

from loom.bst import BST, of
from loom.errors import Invalid


class TestInsert:
    def test_in_order_is_sorted(self):
        assert of([5, 3, 8, 1, 4]).in_order() == [1, 3, 4, 5, 8]

    def test_duplicates_are_not_inserted(self):
        tree = of([1, 2, 2, 1])
        assert len(tree) == 2

    def test_contains(self):
        tree = of([5, 3, 8])
        assert tree.contains(3)
        assert not tree.contains(9)


class TestExtremes:
    def test_minimum_and_maximum(self):
        tree = of([5, 3, 8, 1, 9])
        assert tree.minimum() == 1
        assert tree.maximum() == 9

    def test_an_empty_tree_has_no_extremes(self):
        with pytest.raises(Invalid):
            BST().minimum()
        with pytest.raises(Invalid):
            BST().maximum()


class TestStrings:
    def test_it_sorts_strings(self):
        assert of(["cherry", "apple", "banana"]).in_order() == [
            "apple",
            "banana",
            "cherry",
        ]
