from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.lru import LRUCache


class TestCache:
    def test_get_and_put(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_a_miss_returns_the_default(self):
        assert LRUCache(2).get("x", "fallback") == "fallback"

    def test_the_least_recently_used_is_evicted(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_getting_refreshes_recency(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")
        cache.put("c", 3)
        assert cache.get("a") == 1
        assert cache.get("b") is None

    def test_putting_an_existing_key_updates_and_refreshes(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)
        cache.put("c", 3)
        assert cache.get("a") == 10
        assert cache.get("b") is None


class TestGuards:
    def test_a_zero_capacity_is_refused(self):
        with pytest.raises(Invalid):
            LRUCache(0)

    def test_len_and_contains(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        assert len(cache) == 1
        assert "a" in cache
