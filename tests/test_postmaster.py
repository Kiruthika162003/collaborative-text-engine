from __future__ import annotations

import pytest

from loom.author import Author
from loom.binder import Binder
from loom.errors import Torn
from loom.marks import Mark, Wardrobe
from loom.postmaster import (
    Postmaster,
    encode_binder_write,
    encode_mark,
)
from loom.registers import Write
from loom.station import Station
from loom.wire import encode


def sorting_office() -> Postmaster:
    station = Station.named("bob")
    return Postmaster(
        station=station,
        wardrobe=Wardrobe(weave=station.author.weave),
        binder=Binder(),
    )


def alice_pages():
    alice = Author(site="alice")
    ops = alice.type_at(0, "bold words")
    mark = Mark(
        id=alice._mint(),
        style="bold",
        start=ops[0].id,
        end=ops[3].id,
    )
    return ops, mark


class TestRouting:
    def test_text_attire_and_binder_share_one_wire(
        self,
    ):
        office = sorting_office()
        ops, mark = alice_pages()
        for op in ops:
            office.dispatch(encode(op))
        office.dispatch(encode_mark(mark))
        office.dispatch(
            encode_binder_write(
                "ttl",
                Write(
                    site="alice",
                    rank=3,
                    value="The|Piped Title",
                ),
            )
        )
        assert office.station.text() == "bold words"
        assert office.wardrobe.spans()[0] == (
            "bold",
            frozenset({"bold"}),
        )
        assert office.binder.title.read() == (
            "The|Piped Title"
        )
        assert (
            "attire: 1, binder: 1, text: 10"
        ) in office.ledger()

    def test_status_routes_to_every_voice(self):
        office = sorting_office()
        office.dispatch(
            encode_binder_write(
                "sts",
                Write(
                    site="alice", rank=2, value="draft"
                ),
            )
        )
        assert office.binder.status.page() == (
            "settled: 'draft' by alice"
        )


class TestTheAttireShelf:
    def test_a_mark_waits_for_its_pins(self):
        office = sorting_office()
        ops, mark = alice_pages()
        receipt = office.dispatch(encode_mark(mark))
        assert "its pins have not arrived" in receipt
        receipts = [
            office.dispatch(encode(op)) for op in ops
        ]
        assert (
            "1 attire item(s) drained off the shelf"
        ) in receipts[3]
        assert office.attire_shelf == []
        assert office.wardrobe.census().startswith(
            "1 mark(s) standing"
        )


class TestTornEnvelopes:
    def test_the_verbs_are_a_closed_set(self):
        office = sorting_office()
        with pytest.raises(Torn) as caught:
            office.dispatch("hug|alice:1")
        assert "guesses at no addresses" in str(
            caught.value
        )

    def test_short_envelopes_are_torn(self):
        office = sorting_office()
        with pytest.raises(Torn):
            office.dispatch("mrk|alice:1|bold")
        with pytest.raises(Torn):
            office.dispatch("ttl|alice|3")
        with pytest.raises(Torn):
            encode_binder_write(
                "sub",
                Write(site="a", rank=1, value="x"),
            )
