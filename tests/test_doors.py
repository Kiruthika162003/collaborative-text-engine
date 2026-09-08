from __future__ import annotations

import pytest

from loom.author import Author
from loom.doors import Doorkeeper
from loom.errors import Invalid
from loom.station import Station


def knocking_ops():
    alice = Author(site="alice")
    return alice.type_at(0, "hi")


class TestScreening:
    def test_writers_pass_with_the_door_open(self):
        door = Doorkeeper()
        door.admit("alice", "writer", by="host")
        for op in knocking_ops():
            assert "the door stands open" in (
                door.screen(op)
            )

    def test_a_readers_own_ops_are_refused_by_name(
        self,
    ):
        door = Doorkeeper()
        door.admit("alice", "reader", by="host")
        with pytest.raises(Invalid) as caught:
            door.screen(knocking_ops()[0])
        message = str(caught.value)
        assert "alice holds a reader's role" in message
        assert "judges hands, not words" in message
        assert door.turned_away == 1

    def test_the_open_house_welcomes_strangers(self):
        door = Doorkeeper(policy="open")
        assert "stands open" in door.screen(
            knocking_ops()[0]
        )

    def test_the_closed_house_holds_the_threshold(self):
        door = Doorkeeper(policy="closed")
        with pytest.raises(Invalid) as caught:
            door.screen(knocking_ops()[0])
        assert "closed-house policy" in str(caught.value)

    def test_shears_are_judged_like_any_hand(self):
        alice = Author(site="alice")
        alice.type_at(0, "ab")
        shear = alice.erase_at(0, 1)[0]
        door = Doorkeeper(policy="closed")
        with pytest.raises(Invalid):
            door.screen(shear)


class TestTheHouse:
    def test_promotion_opens_the_door_mid_session(self):
        door = Doorkeeper(policy="closed")
        station = Station.named("bob")
        alice = Author(site="alice")
        ops = alice.type_at(0, "later")
        with pytest.raises(Invalid):
            door.screen(ops[0])
        door.admit("alice", "writer", by="host")
        for op in ops:
            door.screen(op)
            station.hear(op)
        assert station.text() == "later"

    def test_demotion_is_remembered_out_loud(self):
        door = Doorkeeper()
        door.admit("alice", "writer", by="host")
        entry = door.admit("alice", "reader", by="host")
        assert entry.startswith("DEMOTED: alice")
        page = door.page()
        assert "DEMOTED: alice to reader by host" in (
            page
        )

    def test_the_page_counts_the_turned_away(self):
        door = Doorkeeper(policy="closed")
        for op in knocking_ops():
            with pytest.raises(Invalid):
                door.screen(op)
        assert "2 turned away" in door.page()

    def test_roles_are_a_closed_vocabulary(self):
        with pytest.raises(Invalid):
            Doorkeeper().admit(
                "alice", "editor", by="host"
            )
        with pytest.raises(Invalid):
            Doorkeeper(policy="ajar")
