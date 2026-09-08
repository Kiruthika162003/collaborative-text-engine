from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.ids import OpId
from loom.orset import Basket, Pluck, Sprig


def dot(site: str, counter: int) -> OpId:
    return OpId(site=site, counter=counter)


class TestAdding:
    def test_items_land_under_their_dots(self):
        basket = Basket()
        basket.add(
            Sprig(dot=dot("alice", 1), item="urgent")
        )
        assert basket.has("urgent")
        assert basket.items() == ["urgent"]

    def test_two_dots_one_item(self):
        basket = Basket()
        basket.add(
            Sprig(dot=dot("alice", 1), item="urgent")
        )
        basket.add(
            Sprig(dot=dot("bob", 1), item="urgent")
        )
        assert basket.items() == ["urgent"]
        assert "1 item(s) on 2 dot(s)" in (
            basket.census()
        )

    def test_air_is_refused(self):
        with pytest.raises(Invalid):
            Sprig(dot=dot("alice", 1), item="  ")


class TestPlucking:
    def test_removal_needs_every_receipt(self):
        basket = Basket()
        basket.add(
            Sprig(dot=dot("alice", 1), item="urgent")
        )
        basket.add(
            Sprig(dot=dot("bob", 1), item="urgent")
        )
        basket.pluck(
            Pluck(
                id=dot("cara", 1),
                dots=frozenset({dot("alice", 1)}),
            )
        )
        assert basket.has("urgent")
        basket.pluck(
            Pluck(
                id=dot("cara", 2),
                dots=frozenset({dot("bob", 1)}),
            )
        )
        assert not basket.has("urgent")

    def test_the_concurrent_reads_survives(self):
        basket = Basket()
        basket.add(
            Sprig(dot=dot("alice", 1), item="urgent")
        )
        observed = basket.dots_of("urgent")
        basket.add(
            Sprig(dot=dot("bob", 9), item="urgent")
        )
        receipt = basket.pluck(
            Pluck(id=dot("cara", 1), dots=observed)
        )
        assert "survives on purpose" in receipt
        assert basket.has("urgent")

    def test_arrival_order_tells_the_same_basket(self):
        sprig = Sprig(
            dot=dot("alice", 1), item="urgent"
        )
        removal = Pluck(
            id=dot("bob", 1),
            dots=frozenset({dot("alice", 1)}),
        )
        one = Basket()
        one.add(sprig)
        one.pluck(removal)
        two = Basket()
        two.pluck(removal)
        receipt = two.add(sprig)
        assert "arrives already plucked" in receipt
        assert one.items() == two.items() == []

    def test_receipts_apply_once(self):
        basket = Basket()
        basket.add(
            Sprig(dot=dot("alice", 1), item="urgent")
        )
        removal = Pluck(
            id=dot("bob", 1),
            dots=frozenset({dot("alice", 1)}),
        )
        basket.pluck(removal)
        assert "one receipt, one removal" in (
            basket.pluck(removal)
        )
