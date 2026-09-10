from __future__ import annotations

import random

from loom.splay import SplayTree


class TestSetBehaviour:
    def test_insert_and_membership(self):
        tree = SplayTree()
        for key in (5, 3, 8, 1, 4):
            assert tree.insert(key)
        assert 4 in tree
        assert 9 not in tree
        assert len(tree) == 5

    def test_a_duplicate_insert_is_a_no_op(self):
        tree = SplayTree()
        assert tree.insert(7)
        assert not tree.insert(7)
        assert len(tree) == 1

    def test_items_come_back_in_order(self):
        tree = SplayTree()
        for key in (5, 3, 8, 1, 4, 7, 9, 2, 6):
            tree.insert(key)
        assert tree.items() == [1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestRemove:
    def test_remove_a_key(self):
        tree = SplayTree()
        for key in (5, 3, 8, 1, 4, 7):
            tree.insert(key)
        assert tree.remove(3)
        assert 3 not in tree
        assert tree.items() == [1, 4, 5, 7, 8]

    def test_removing_an_absent_key_reports_false(self):
        tree = SplayTree()
        tree.insert(1)
        assert not tree.remove(2)

    def test_remove_the_only_key(self):
        tree = SplayTree()
        tree.insert(1)
        assert tree.remove(1)
        assert len(tree) == 0
        assert tree.items() == []


class TestSelfAdjustment:
    def test_repeated_access_keeps_correctness(self):
        tree = SplayTree()
        for key in range(50):
            tree.insert(key)
        # Hammer a few keys; the tree reshapes but stays correct.
        for _ in range(200):
            assert 42 in tree
            assert 7 in tree
        assert tree.items() == list(range(50))

    def test_sorted_insertion_does_not_break(self):
        tree = SplayTree()
        for key in range(200):
            tree.insert(key)
        assert tree.items() == list(range(200))
        assert 150 in tree


class TestAgainstASet:
    def test_matches_a_sorted_set_over_random_ops(self):
        tree = SplayTree()
        shadow: set = set()
        rng = random.Random(31)
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
