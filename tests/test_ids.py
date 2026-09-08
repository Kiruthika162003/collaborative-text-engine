from __future__ import annotations

import pytest

from loom.errors import Invalid, Torn
from loom.ids import OpId, check_site, mint_after


class TestSiteNames:
    def test_the_door_admits_the_plain(self):
        assert check_site("alice") == "alice"
        assert check_site("site-7") == "site-7"

    def test_the_door_refuses_the_unrenderable(self):
        for wrong in ("", "Alice", "a:b", "7up", "a b"):
            with pytest.raises(Invalid):
                check_site(wrong)


class TestOrdering:
    def test_counter_first_respects_causality(self):
        earlier = OpId(site="zed", counter=1)
        later = OpId(site="alice", counter=2)
        assert earlier < later

    def test_site_second_breaks_true_ties(self):
        left = OpId(site="alice", counter=3)
        right = OpId(site="bob", counter=3)
        assert left < right
        assert sorted([right, left]) == [left, right]

    def test_equal_ids_are_equal(self):
        assert OpId(site="alice", counter=3) == OpId(
            site="alice", counter=3
        )


class TestWireForm:
    def test_round_trip_is_identity(self):
        original = OpId(site="alice", counter=42)
        assert OpId.parse(original.wire()) == original

    def test_the_form_is_boring_on_purpose(self):
        assert OpId(site="bob", counter=7).wire() == (
            "bob:7"
        )

    def test_torn_wire_is_named_torn(self):
        with pytest.raises(Torn):
            OpId.parse("no-separator")
        with pytest.raises(Torn):
            OpId.parse("alice:not-a-number")


class TestMinting:
    def test_the_next_id_follows_what_was_seen(self):
        minted = mint_after("alice", 41)
        assert minted == OpId(site="alice", counter=42)

    def test_counters_start_at_one(self):
        assert mint_after("alice", 0).counter == 1
        with pytest.raises(Invalid):
            OpId(site="alice", counter=0)

    def test_negative_sight_is_refused(self):
        with pytest.raises(Invalid):
            mint_after("alice", -1)
