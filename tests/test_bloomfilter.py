from __future__ import annotations

import pytest

from loom.bloomfilter import BloomFilter
from loom.errors import Invalid


def loaded() -> BloomFilter:
    bloom = BloomFilter(size=10007, hashes=4)
    for word in ["apple", "banana", "cherry"]:
        bloom.add(word)
    return bloom


class TestMembership:
    def test_members_are_always_present(self):
        bloom = loaded()
        assert all(bloom.contains(w) for w in ["apple", "banana", "cherry"])

    def test_an_empty_filter_holds_nothing(self):
        assert not BloomFilter(100).contains("anything")

    def test_a_clear_non_member_is_absent(self):
        # with a large filter and few items, these do not collide
        bloom = loaded()
        assert not bloom.contains("dog")
        assert not bloom.contains("zebra")

    def test_the_in_operator_works(self):
        bloom = loaded()
        assert "apple" in bloom
        assert "dog" not in bloom


class TestGuards:
    def test_a_zero_size_is_refused(self):
        with pytest.raises(Invalid):
            BloomFilter(0)

    def test_a_zero_hash_count_is_refused(self):
        with pytest.raises(Invalid):
            BloomFilter(100, hashes=0)
