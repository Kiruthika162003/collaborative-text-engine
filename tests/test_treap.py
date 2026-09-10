from __future__ import annotations

import random

from loom.treap import Treap


class TestSetBehaviour:
    def test_insert_and_membership(self):
        treap = Treap(seed=1)
        for key in (5, 3, 8, 1, 4):
            assert treap.insert(key)
        assert 4 in treap
        assert 9 not in treap
        assert len(treap) == 5

    def test_a_duplicate_insert_is_a_no_op(self):
        treap = Treap(seed=1)
        assert treap.insert(7)
        assert not treap.insert(7)
        assert len(treap) == 1

    def test_items_come_back_sorted(self):
        treap = Treap(seed=2)
        for key in (5, 3, 8, 1, 4, 7, 9, 2, 6):
            treap.insert(key)
        assert treap.items() == [1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestRemove:
    def test_remove_a_key(self):
        treap = Treap(seed=3)
        for key in (5, 3, 8, 1, 4, 7):
            treap.insert(key)
        assert treap.remove(3)
        assert 3 not in treap
        assert treap.items() == [1, 4, 5, 7, 8]
        assert treap.is_heap_ordered()

    def test_removing_an_absent_key_reports_false(self):
        treap = Treap(seed=3)
        treap.insert(1)
        assert not treap.remove(2)


class TestInvariants:
    def test_heap_order_holds_after_churn(self):
        treap = Treap(seed=5)
        rng = random.Random(5)
        keys = list(range(300))
        rng.shuffle(keys)
        for key in keys:
            treap.insert(key)
        rng.shuffle(keys)
        for key in keys[:150]:
            treap.remove(key)
        assert treap.is_heap_ordered()
        assert treap.items() == sorted(keys[150:])


class TestAgainstASet:
    def test_matches_a_sorted_set_over_random_ops(self):
        treap = Treap(seed=99)
        shadow: set = set()
        rng = random.Random(99)
        for _ in range(2000):
            key = rng.randrange(50)
            if rng.random() < 0.6:
                treap.insert(key)
                shadow.add(key)
            else:
                treap.remove(key)
                shadow.discard(key)
        assert treap.items() == sorted(shadow)
        assert len(treap) == len(shadow)
        assert treap.is_heap_ordered()
