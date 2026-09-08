from __future__ import annotations

import pytest

from loom.clock import VersionVector
from loom.errors import Invalid
from loom.pruner import Pruner
from loom.station import Station


def two_synced() -> tuple[Station, Station]:
    alice = Station.named("alice")
    bob = Station.named("bob")
    for op in alice.type_at(0, "shared draft"):
        bob.hear(op)
    return alice, bob


class TestPruning:
    def test_below_the_horizon_is_forgotten(self):
        alice, bob = two_synced()
        pruner = Pruner()
        horizon = pruner.safe_horizon(
            [alice.clock(), bob.clock()]
        )
        receipt = pruner.prune(alice.journal, horizon)
        assert "pruned 12 of 12" in receipt
        assert alice.journal.size() == 0

    def test_the_weave_is_untouched_by_pruning(self):
        alice, bob = two_synced()
        pruner = Pruner()
        horizon = pruner.safe_horizon(
            [alice.clock(), bob.clock()]
        )
        pruner.prune(alice.journal, horizon)
        assert alice.text() == "shared draft"

    def test_above_the_horizon_is_kept_for_laggards(
        self,
    ):
        alice, bob = two_synced()
        alice.type_at(12, " more")
        pruner = Pruner()
        horizon = pruner.safe_horizon(
            [alice.clock(), bob.clock()]
        )
        pruner.prune(alice.journal, horizon)
        assert alice.journal.size() == 5
        missing = alice.ops_missing_for(bob.clock())
        assert len(missing) == 5

    def test_a_horizon_over_nobody_is_refused(self):
        with pytest.raises(Invalid):
            Pruner().safe_horizon([])


class TestTheHorizon:
    def test_the_floor_is_the_slowest_replica(self):
        pruner = Pruner()
        floor = pruner.safe_horizon(
            [
                VersionVector(
                    seen={"alice": 9, "bob": 3}
                ),
                VersionVector(
                    seen={"alice": 4, "bob": 7}
                ),
            ]
        )
        assert floor.seen == {"alice": 4, "bob": 3}
