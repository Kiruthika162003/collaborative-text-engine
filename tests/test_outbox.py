from __future__ import annotations

from loom.author import Author
from loom.mailroom import Mailroom
from loom.outbox import Outbox


def filled() -> tuple[Author, Outbox]:
    author = Author(site="alice")
    box = Outbox()
    box.hold_many(author.type_at(0, "hello"))
    return author, box


class TestHolding:
    def test_operations_wait_then_flush_in_order(self):
        _author, box = filled()
        assert not box.is_empty()
        batch = box.flush()
        assert [op.id.counter for op in batch] == [
            1,
            2,
            3,
            4,
            5,
        ]
        assert box.is_empty()

    def test_exact_duplicates_are_dropped(self):
        _author, box = filled()
        first = box.peek()[0]
        receipt = box.hold(first)
        assert "already held" in receipt
        assert len(box.peek()) == 5

    def test_the_batch_delivers_and_converges(self):
        _author, box = filled()
        bob = Author(site="bob")
        room = Mailroom(author=bob)
        for op in box.flush():
            room.receive(op)
        assert bob.text() == "hello"

    def test_an_insert_and_its_shear_both_ship(self):
        author = Author(site="alice")
        box = Outbox()
        typed = author.type_at(0, "ab")
        box.hold_many(typed)
        box.hold_many(author.erase_at(0, 1))
        batch = box.flush()
        assert len(batch) == 3
        bob = Author(site="bob")
        room = Mailroom(author=bob)
        for op in batch:
            room.receive(op)
        assert bob.text() == "b"


class TestTheLedger:
    def test_the_high_water_records_the_fullest(self):
        author = Author(site="alice")
        box = Outbox()
        box.hold_many(author.type_at(0, "abcd"))
        box.flush()
        box.hold_many(author.type_at(4, "e"))
        assert "high-water 4" in box.ledger()

    def test_the_ledger_counts_shipped(self):
        _author, box = filled()
        box.flush()
        assert "5 shipped" in box.ledger()
        assert "never for convergence" in box.ledger()
