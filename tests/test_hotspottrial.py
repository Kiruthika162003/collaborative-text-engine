from __future__ import annotations

from loom.trials.hotspottrial import run


class TestHotspottrial:
    def test_the_verdict_holds(self):
        assert run().holds

    def test_the_storm_produced_hotspots(self):
        assert run().numbers["hotspots"] > 0

    def test_the_confluences_agree(self):
        assert run().numbers["one_digest"]

    def test_both_hands_were_in_contention(self):
        assert run().numbers["sites_in_contention"] == ["alice", "bob"]
