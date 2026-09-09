from __future__ import annotations

import pytest

from loom.bitset import BitSet, of
from loom.errors import Invalid


class TestMembership:
    def test_add_and_contains(self):
        bits = of([1, 3, 5])
        assert 3 in bits
        assert 2 not in bits

    def test_remove(self):
        bits = of([1, 2, 3])
        bits.remove(2)
        assert 2 not in bits

    def test_members_are_ordered(self):
        assert of([5, 1, 3]).members() == [1, 3, 5]

    def test_count(self):
        assert len(of([1, 2, 3])) == 3

    def test_a_negative_member_is_refused(self):
        with pytest.raises(Invalid):
            BitSet().add(-1)


class TestSetOps:
    def test_union(self):
        assert of([1, 2]).union(of([2, 3])).members() == [1, 2, 3]

    def test_intersection(self):
        assert of([1, 2, 3]).intersection(of([2, 3, 4])).members() == [2, 3]

    def test_difference(self):
        assert of([1, 2, 3]).difference(of([2])).members() == [1, 3]


class TestLarge:
    def test_a_large_member_is_fine(self):
        bits = BitSet().add(1000)
        assert 1000 in bits
        assert len(bits) == 1
