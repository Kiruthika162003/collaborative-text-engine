from __future__ import annotations

import random

import pytest

from loom.errors import Invalid
from loom.indexedheap import IndexedHeap


class TestOrdering:
    def test_pops_in_priority_order(self):
        heap = IndexedHeap()
        for item, priority in [("a", 5), ("b", 1), ("c", 3), ("d", 2)]:
            heap.push(item, priority)
        assert [heap.pop_min() for _ in range(4)] == ["b", "d", "c", "a"]

    def test_peek_shows_the_minimum(self):
        heap = IndexedHeap()
        heap.push("x", 10)
        heap.push("y", 4)
        assert heap.peek() == "y"
        assert len(heap) == 2

    def test_membership_and_priority(self):
        heap = IndexedHeap()
        heap.push("x", 7)
        assert "x" in heap
        assert heap.priority("x") == 7
        assert "z" not in heap


class TestDecreaseKey:
    def test_lowering_reorders(self):
        heap = IndexedHeap()
        heap.push("a", 5)
        heap.push("b", 3)
        heap.decrease_key("a", 1)
        assert heap.pop_min() == "a"

    def test_raising_is_refused(self):
        heap = IndexedHeap()
        heap.push("a", 5)
        with pytest.raises(Invalid):
            heap.decrease_key("a", 9)

    def test_push_or_decrease_inserts_then_lowers(self):
        heap = IndexedHeap()
        heap.push_or_decrease("a", 5)
        heap.push_or_decrease("a", 2)
        heap.push_or_decrease("a", 8)  # ignored, higher
        assert heap.priority("a") == 2


class TestGuards:
    def test_a_duplicate_push_is_refused(self):
        heap = IndexedHeap()
        heap.push("a", 1)
        with pytest.raises(Invalid):
            heap.push("a", 2)

    def test_popping_empty_is_refused(self):
        with pytest.raises(Invalid):
            IndexedHeap().pop_min()


class TestAgainstSorted:
    def test_matches_a_sorted_drain_over_random_pushes(self):
        rng = random.Random(13)
        heap = IndexedHeap()
        pairs = {}
        for i in range(500):
            item = f"item{i}"
            priority = rng.randrange(10000)
            heap.push(item, priority)
            pairs[item] = priority
        drained = [heap.pop_min() for _ in range(len(pairs))]
        assert set(drained) == set(pairs)
        assert [pairs[item] for item in drained] == sorted(pairs.values())
