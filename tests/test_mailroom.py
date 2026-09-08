from __future__ import annotations

from loom.author import Author
from loom.mailroom import Mailroom


def wired_pair() -> tuple[Author, Author, Mailroom]:
    alice = Author(site="alice")
    bob = Author(site="bob")
    return alice, bob, Mailroom(author=bob)


class TestDelivery:
    def test_in_order_arrivals_weave_directly(self):
        alice, bob, mailroom = wired_pair()
        for op in alice.type_at(0, "hi"):
            receipt = mailroom.receive(op)
            assert "woven at slot" in receipt
        assert bob.text() == "hi"

    def test_reordered_arrivals_wait_then_weave(self):
        alice, bob, mailroom = wired_pair()
        ops = alice.type_at(0, "abc")
        shelved = mailroom.receive(ops[2])
        assert "shelved" in shelved
        assert "waiting for alice:1" in shelved
        mailroom.receive(ops[1])
        receipt = mailroom.receive(ops[0])
        assert "drained 2 shelved arrival(s)" in receipt
        assert bob.text() == "abc"
        assert (
            "every arrival found its moment"
            in mailroom.shelf_report()
        )

    def test_a_shear_waits_for_its_target(self):
        alice, bob, mailroom = wired_pair()
        typed = alice.type_at(0, "ab")
        shears = alice.erase_at(0, 1)
        held = mailroom.receive(shears[0])
        assert "waiting for alice:1" in held
        for op in typed:
            mailroom.receive(op)
        assert bob.text() == "b"


class TestRepeats:
    def test_a_repeating_network_is_being_a_network(
        self,
    ):
        alice, bob, mailroom = wired_pair()
        ops = alice.type_at(0, "ok")
        for op in ops:
            mailroom.receive(op)
        receipt = mailroom.receive(ops[0])
        assert "is a repeat" in receipt
        assert bob.text() == "ok"
        assert mailroom.duplicates == 1

    def test_a_shelved_repeat_is_swept_as_a_repeat(self):
        alice, _bob, mailroom = wired_pair()
        ops = alice.type_at(0, "ab")
        mailroom.receive(ops[1])
        mailroom.receive(ops[1])
        mailroom.receive(ops[0])
        assert mailroom.duplicates >= 1
        assert mailroom.shelf == []


class TestTheLedger:
    def test_the_ledger_counts_all_three_columns(self):
        alice, _bob, mailroom = wired_pair()
        ops = alice.type_at(0, "abc")
        mailroom.receive(ops[2])
        mailroom.receive(ops[0])
        mailroom.receive(ops[0])
        assert mailroom.ledger() == (
            "1 woven, 1 repeat(s), 1 still waiting"
        )
        report = mailroom.shelf_report()
        assert "alice:3" in report
        assert "waiting for alice:2" in report
