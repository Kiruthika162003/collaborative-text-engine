from __future__ import annotations

from loom.handshake import gossip, shake
from loom.snapshot import same_fabric
from loom.station import Station


def diverged_pair() -> tuple[Station, Station]:
    alice = Station.named("alice")
    bob = Station.named("bob")
    for op in alice.type_at(0, "shared "):
        bob.hear(op)
    alice.type_at(7, "alice-part")
    bob.type_at(7, "bob-part")
    return alice, bob


class TestTheShake:
    def test_offline_divergence_settles_both_ways(self):
        alice, bob = diverged_pair()
        receipt = shake(alice, bob)
        assert "settled in" in receipt
        assert "10 op(s) to bob" in receipt
        assert "8 op(s) to alice" in receipt
        assert alice.text() == bob.text()
        assert same_fabric(
            alice.author.weave, bob.author.weave
        )

    def test_equal_clocks_ship_nothing(self):
        alice, bob = diverged_pair()
        shake(alice, bob)
        receipt = shake(alice, bob)
        assert receipt.endswith("peace; nothing to ship")

    def test_the_journal_remembers_for_others(self):
        alice, bob = diverged_pair()
        shake(alice, bob)
        cara = Station.named("cara")
        receipt = shake(bob, cara)
        assert "op(s) to cara" in receipt
        assert cara.text() == alice.text()

    def test_shelved_arrivals_still_get_journaled(self):
        alice = Station.named("alice")
        bob = Station.named("bob")
        ops = alice.type_at(0, "abc")
        bob.hear(ops[2])
        assert bob.journal.size() == 1
        assert len(bob.mailroom.shelf) == 1
        for op in ops[:2]:
            bob.hear(op)
        assert bob.text() == "abc"


class TestGossip:
    def test_one_gossip_round_settles_three_stations(
        self,
    ):
        alice = Station.named("alice")
        bob = Station.named("bob")
        cara = Station.named("cara")
        alice.type_at(0, "a-line ")
        bob.type_at(0, "b-line ")
        cara.type_at(0, "c-line ")
        page = gossip([alice, bob, cara])
        assert page.count("settled in") >= 2
        texts = {
            alice.text(), bob.text(), cara.text()
        }
        assert len(texts) == 1
        assert same_fabric(
            alice.author.weave, cara.author.weave
        )
