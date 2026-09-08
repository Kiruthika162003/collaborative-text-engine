from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.presence import Presence


class TestHeartbeats:
    def test_a_recent_beat_is_present(self):
        room = Presence(timeout=30)
        room.beat("alice", 10)
        room.tick(20)
        assert room.is_present("alice")

    def test_a_stale_beat_goes_away(self):
        room = Presence(timeout=30)
        room.beat("alice", 10)
        room.tick(50)
        assert not room.is_present("alice")
        assert "alice" in room.away()

    def test_an_unheard_hand_is_absent(self):
        room = Presence()
        assert not room.is_present("ghost")

    def test_a_fresh_beat_revives_presence(self):
        room = Presence(timeout=30)
        room.beat("alice", 10)
        room.tick(50)
        room.beat("alice", 50)
        assert room.is_present("alice")


class TestGhosts:
    def test_a_past_beat_cannot_revive(self):
        room = Presence()
        room.beat("alice", 40)
        with pytest.raises(Invalid) as caught:
            room.beat("alice", 10)
        assert "cannot revive a hand" in str(
            caught.value
        )

    def test_a_backward_tick_is_refused(self):
        room = Presence()
        room.tick(40)
        with pytest.raises(Invalid):
            room.tick(10)


class TestTheRoster:
    def test_the_roster_splits_here_from_away(self):
        room = Presence(timeout=20)
        room.beat("alice", 5)
        room.beat("bob", 45)
        room.tick(50)
        page = room.roster()
        assert "1 here, 1 away" in page
        assert "bob: present" in page
        assert "alice: away, last seen tick 5" in page
