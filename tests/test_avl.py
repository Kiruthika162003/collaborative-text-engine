from __future__ import annotations

import random

import pytest

from loom.avl import AVLTree


class TestSetBehaviour:
    def test_insert_and_membership(self):
        tree = AVLTree()
        for key in (5, 3, 8, 1, 4):
            assert tree.insert(key)
        assert 4 in tree
        assert 9 not in tree
        assert len(tree) == 5

    def test_a_duplicate_insert_is_a_no_op(self):
        tree = AVLTree()
        assert tree.insert(7)
        assert not tree.insert(7)
        assert len(tree) == 1

    def test_items_come_back_in_order(self):
        tree = AVLTree()
        for key in (5, 3, 8, 1, 4, 7, 9, 2, 6):
            tree.insert(key)
        assert tree.items() == [1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestBalance:
    def test_sorted_insertion_stays_short(self):
        tree = AVLTree()
        for key in range(1, 128):
            tree.insert(key)
        assert tree.is_balanced()
        # A chain of 127 would be height 127; balanced is near log2(127).
        assert tree.height() <= 8

    def test_balanced_after_random_churn(self):
        tree = AVLTree()
        rng = random.Random(1234)
        keys = list(range(200))
        rng.shuffle(keys)
        for key in keys:
            tree.insert(key)
        rng.shuffle(keys)
        for key in keys[:100]:
            tree.remove(key)
        assert tree.is_balanced()
        assert tree.items() == sorted(keys[100:])


class TestRemove:
    def test_remove_a_leaf_and_an_internal_node(self):
        tree = AVLTree()
        for key in (5, 3, 8, 1, 4, 7, 9):
            tree.insert(key)
        assert tree.remove(1)
        assert tree.remove(8)
        assert 1 not in tree
        assert 8 not in tree
        assert tree.items() == [3, 4, 5, 7, 9]
        assert tree.is_balanced()

    def test_removing_an_absent_key_reports_false(self):
        tree = AVLTree()
        tree.insert(1)
        assert not tree.remove(2)
        assert len(tree) == 1


class TestExtremes:
    def test_minimum_and_maximum(self):
        tree = AVLTree()
        for key in (5, 3, 8, 1, 9):
            tree.insert(key)
        assert tree.minimum() == 1
        assert tree.maximum() == 9

    def test_an_empty_tree_has_no_extreme(self):
        with pytest.raises(ValueError):
            AVLTree().minimum()


class TestAgainstSorted:
    def test_matches_a_sorted_set_over_random_ops(self):
        tree = AVLTree()
        shadow: set = set()
        rng = random.Random(99)
        for _ in range(2000):
            key = rng.randrange(50)
            if rng.random() < 0.6:
                tree.insert(key)
                shadow.add(key)
            else:
                tree.remove(key)
                shadow.discard(key)
        assert tree.items() == sorted(shadow)
        assert len(tree) == len(shadow)
        assert tree.is_balanced()
