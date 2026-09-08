from __future__ import annotations

import pytest

from loom.counters import GrowOnly, PlusMinus


class TestGrowOnly:
    def test_concurrent_increments_all_survive(self):
        one = GrowOnly()
        two = GrowOnly()
        one.increment("alice")
        one.increment("alice")
        two.increment("bob", 3)
        one.merge(two)
        assert one.value() == 5

    def test_merge_is_idempotent(self):
        one = GrowOnly()
        one.increment("alice", 4)
        snapshot = one.copy()
        one.merge(snapshot)
        one.merge(snapshot)
        assert one.value() == 4

    def test_merge_is_commutative(self):
        a = GrowOnly()
        a.increment("alice", 2)
        b = GrowOnly()
        b.increment("bob", 5)
        left = a.copy()
        left.merge(b)
        right = b.copy()
        right.merge(a)
        assert left.value() == right.value() == 7

    def test_a_lost_increment_heals_on_merge(self):
        server = GrowOnly()
        client = GrowOnly()
        client.increment("alice", 9)
        assert server.value() == 0
        server.merge(client)
        assert server.value() == 9

    def test_growth_only_grows(self):
        with pytest.raises(ValueError):
            GrowOnly().increment("alice", -1)


class TestPlusMinus:
    def test_up_and_down_net_out(self):
        counter = PlusMinus()
        counter.increment("alice", 5)
        counter.decrement("bob", 2)
        assert counter.value() == 3

    def test_decrement_below_zero_is_honest(self):
        counter = PlusMinus()
        counter.decrement("alice", 3)
        assert counter.value() == -3

    def test_merge_reconciles_both_directions(self):
        one = PlusMinus()
        one.increment("alice", 4)
        one.decrement("alice", 1)
        two = PlusMinus()
        two.increment("bob", 2)
        two.decrement("bob", 5)
        one.merge(two)
        assert one.value() == 0

    def test_merge_is_commutative_and_idempotent(self):
        a = PlusMinus()
        a.increment("alice", 3)
        a.decrement("alice", 1)
        b = PlusMinus()
        b.increment("bob", 1)
        left = a.copy()
        left.merge(b)
        left.merge(b)
        right = b.copy()
        right.merge(a)
        assert left.value() == right.value() == 3
