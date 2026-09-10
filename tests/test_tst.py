from __future__ import annotations

import random

import pytest

from loom.errors import Invalid
from loom.tst import TernarySearchTree


class TestMembership:
    def test_insert_and_contains(self):
        tree = TernarySearchTree()
        for word in ("she", "sells", "sea", "shells"):
            tree.insert(word)
        assert "she" in tree
        assert "sea" in tree
        assert "shell" not in tree
        assert "s" not in tree
        assert len(tree) == 4

    def test_values_are_stored(self):
        tree = TernarySearchTree()
        tree.insert("one", 1)
        tree.insert("two", 2)
        assert tree.get("one") == 1
        assert tree.get("two") == 2
        assert tree.get("three") is None

    def test_reinsert_updates_without_growing(self):
        tree = TernarySearchTree()
        tree.insert("key", 1)
        tree.insert("key", 2)
        assert tree.get("key") == 2
        assert len(tree) == 1

    def test_the_empty_string_is_refused(self):
        with pytest.raises(Invalid):
            TernarySearchTree().insert("")


class TestKeys:
    def test_keys_come_back_sorted(self):
        tree = TernarySearchTree()
        for word in ("banana", "apple", "cherry", "apricot"):
            tree.insert(word)
        assert tree.keys() == ["apple", "apricot", "banana", "cherry"]

    def test_keys_with_prefix(self):
        tree = TernarySearchTree()
        for word in ("she", "sells", "sea", "shells", "shore"):
            tree.insert(word)
        assert tree.keys_with_prefix("sh") == ["she", "shells", "shore"]

    def test_a_prefix_that_is_itself_a_key(self):
        tree = TernarySearchTree()
        for word in ("go", "gopher", "gone"):
            tree.insert(word)
        assert tree.keys_with_prefix("go") == ["go", "gone", "gopher"]

    def test_an_absent_prefix_gives_nothing(self):
        tree = TernarySearchTree()
        tree.insert("apple")
        assert tree.keys_with_prefix("z") == []


class TestAgainstASet:
    def test_matches_a_set_over_random_words(self):
        rng = random.Random(21)
        tree = TernarySearchTree()
        shadow: set = set()
        for _ in range(500):
            word = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 6)))
            tree.insert(word)
            shadow.add(word)
        assert tree.keys() == sorted(shadow)
        assert len(tree) == len(shadow)
        for word in shadow:
            assert word in tree
