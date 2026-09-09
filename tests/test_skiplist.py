from __future__ import annotations

import random

import pytest

from loom.errors import Invalid
from loom.skiplist import SkipList


class TestSetBehaviour:
    def test_insert_and_membership(self):
        skip = SkipList(seed=1)
        for key in (5, 3, 8, 1, 4):
            assert skip.insert(key)
        assert 4 in skip
        assert 9 not in skip
        assert len(skip) == 5

    def test_a_duplicate_insert_is_a_no_op(self):
        skip = SkipList(seed=1)
        assert skip.insert(7)
        assert not skip.insert(7)
        assert len(skip) == 1

    def test_items_come_back_in_order(self):
        skip = SkipList(seed=2)
        for key in (5, 3, 8, 1, 4, 7, 9, 2, 6):
            skip.insert(key)
        assert skip.items() == [1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestRemove:
    def test_remove_deletes_a_key(self):
        skip = SkipList(seed=3)
        for key in (5, 3, 8, 1, 4):
            skip.insert(key)
        assert skip.remove(3)
        assert 3 not in skip
        assert skip.items() == [1, 4, 5, 8]

    def test_removing_an_absent_key_reports_false(self):
        skip = SkipList(seed=3)
        skip.insert(1)
        assert not skip.remove(2)


class TestShape:
    def test_the_level_stays_modest(self):
        skip = SkipList(max_level=16, seed=5)
        for key in range(1000):
            skip.insert(key)
        # Sorted insertion of 1000 keys should not build a tall tower;
        # log2(1000) is about 10, well under the cap.
        assert skip.level() <= 16

    def test_a_zero_max_level_is_refused(self):
        with pytest.raises(Invalid):
            SkipList(max_level=0)


class TestAgainstSorted:
    def test_matches_a_sorted_set_over_random_ops(self):
        skip = SkipList(seed=99)
        shadow: set = set()
        rng = random.Random(99)
        for _ in range(2000):
            key = rng.randrange(50)
            if rng.random() < 0.6:
                skip.insert(key)
                shadow.add(key)
            else:
                skip.remove(key)
                shadow.discard(key)
        assert skip.items() == sorted(shadow)
        assert len(skip) == len(shadow)
