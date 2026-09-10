from __future__ import annotations

import random

import pytest

from loom.hashmap import HashMap


class TestBasics:
    def test_set_and_get(self):
        table = HashMap()
        table["a"] = 1
        table["b"] = 2
        assert table["a"] == 1
        assert table["b"] == 2
        assert len(table) == 2

    def test_update_an_existing_key(self):
        table = HashMap()
        table["a"] = 1
        table["a"] = 9
        assert table["a"] == 9
        assert len(table) == 1

    def test_missing_key_raises(self):
        table = HashMap()
        with pytest.raises(KeyError):
            _ = table["absent"]

    def test_get_with_default(self):
        table = HashMap()
        table["a"] = 1
        assert table.get("a") == 1
        assert table.get("z", -1) == -1

    def test_contains(self):
        table = HashMap()
        table["a"] = 1
        assert "a" in table
        assert "b" not in table


class TestDeletion:
    def test_delete_removes_a_key(self):
        table = HashMap()
        table["a"] = 1
        del table["a"]
        assert "a" not in table
        assert len(table) == 0

    def test_deleting_a_collision_leaves_neighbours_findable(self):
        # Force collisions with a tiny table and integer keys sharing a slot.
        table = HashMap(capacity=8)
        for key in range(0, 40, 8):  # 0, 8, 16, 24, 32 all hash to slot 0
            table[key] = key
        del table[0]
        for key in (8, 16, 24, 32):
            assert table[key] == key

    def test_deleting_an_absent_key_raises(self):
        table = HashMap()
        with pytest.raises(KeyError):
            del table["absent"]


class TestGrowth:
    def test_survives_many_inserts(self):
        table = HashMap()
        for i in range(1000):
            table[i] = i * i
        assert len(table) == 1000
        for i in range(1000):
            assert table[i] == i * i


class TestAgainstDict:
    def test_matches_a_dict_over_random_ops(self):
        table = HashMap()
        shadow: dict = {}
        rng = random.Random(17)
        for _ in range(5000):
            key = rng.randrange(100)
            roll = rng.random()
            if roll < 0.55:
                value = rng.randrange(1000)
                table[key] = value
                shadow[key] = value
            elif roll < 0.8 and key in shadow:
                del table[key]
                del shadow[key]
            else:
                assert table.get(key) == shadow.get(key)
        assert len(table) == len(shadow)
        assert dict(table.items()) == shadow
