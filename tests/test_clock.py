from __future__ import annotations

import pytest

from loom.clock import VersionVector
from loom.errors import Invalid, Stale, Torn
from loom.ids import OpId


def vector(**tops: int) -> VersionVector:
    return VersionVector(seen=dict(tops))


class TestObservation:
    def test_contiguous_arrivals_are_woven(self):
        clock = VersionVector()
        clock.observe(OpId(site="alice", counter=1))
        clock.observe(OpId(site="alice", counter=2))
        assert clock.top("alice") == 2

    def test_the_past_is_stale(self):
        clock = vector(alice=3)
        with pytest.raises(Stale) as caught:
            clock.observe(OpId(site="alice", counter=2))
        assert "already woven" in str(caught.value)

    def test_the_future_is_a_buffer_cue(self):
        clock = vector(alice=1)
        with pytest.raises(Invalid) as caught:
            clock.observe(OpId(site="alice", counter=3))
        assert "Buffer it" in str(caught.value)
        assert clock.top("alice") == 1

    def test_has_reads_the_prefix(self):
        clock = vector(alice=3)
        assert clock.has(OpId(site="alice", counter=2))
        assert not clock.has(
            OpId(site="alice", counter=4)
        )


class TestComparison:
    def test_the_three_answers_of_distributed_time(self):
        bigger = vector(alice=3, bob=2)
        smaller = vector(alice=1, bob=2)
        sideways = vector(alice=1, bob=5)
        assert bigger.dominates(smaller)
        assert not smaller.dominates(bigger)
        assert smaller.concurrent_with(sideways) is False
        assert bigger.concurrent_with(sideways)

    def test_a_vector_dominates_itself(self):
        clock = vector(alice=2)
        assert clock.dominates(clock.copy())
        assert not clock.concurrent_with(clock.copy())


class TestMerge:
    def test_pointwise_maximum_and_the_count(self):
        ours = vector(alice=3, bob=1)
        theirs = vector(bob=4, cara=2)
        receipt = ours.merge(theirs)
        assert "2 site(s) advanced" in receipt
        assert ours.seen == {
            "alice": 3,
            "bob": 4,
            "cara": 2,
        }

    def test_merge_never_rewinds(self):
        ours = vector(alice=5)
        ours.merge(vector(alice=2))
        assert ours.top("alice") == 5


class TestWireForm:
    def test_equal_vectors_render_equal_strings(self):
        one = vector(bob=2, alice=1)
        two = vector(alice=1, bob=2)
        assert one.wire() == two.wire()
        assert one.wire() == "@alice:1,bob:2"

    def test_round_trip_is_identity(self):
        original = vector(alice=3, bob=7)
        parsed = VersionVector.parse(original.wire())
        assert parsed.seen == original.seen
        assert VersionVector.parse("@empty").seen == {}

    def test_two_opinions_are_not_a_clock(self):
        with pytest.raises(Torn) as caught:
            VersionVector.parse("@alice:1,alice:2")
        assert "two opinions" in str(caught.value)

    def test_a_vector_opens_with_at(self):
        with pytest.raises(Torn):
            VersionVector.parse("alice:1")
