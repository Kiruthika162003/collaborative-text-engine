from __future__ import annotations

from loom.author import Author
from loom.mailroom import Mailroom
from loom.tapediff import (
    diff,
    divergence_by_site,
    report,
)
from loom.transcript import Tape


def diverged() -> tuple[Tape, Tape]:
    shared = Tape()
    alice = Author(site="alice", tape=shared)
    base = alice.type_at(0, "base ")
    bob = Author(site="bob", tape=Tape())
    room = Mailroom(author=bob)
    for op in base:
        room.receive(op)
    alice.type_at(5, "alice")
    bob.type_at(5, "bob")
    return alice.tape, bob.tape


class TestDiffing:
    def test_the_three_regions_are_named(self):
        left, right = diverged()
        result = diff(left, right)
        assert len(result.shared) == 5
        assert len(result.only_left) == 5
        assert len(result.only_right) == 3

    def test_identical_tapes_have_empty_wings(self):
        left, _right = diverged()
        result = diff(left, left)
        assert result.only_left == []
        assert result.only_right == []

    def test_a_reorder_that_reads_alike_is_no_diff(self):
        shared = Tape()
        alice = Author(site="alice", tape=shared)
        ops = alice.type_at(0, "abc")
        reordered = Tape(
            reel=[ops[0], ops[2], ops[1]]
        )
        result = diff(shared, reordered)
        assert result.only_left == []
        assert result.only_right == []


class TestBreakdown:
    def test_divergence_is_attributed_by_site(self):
        left, right = diverged()
        counts = divergence_by_site(left, right)
        assert counts == {"alice": 5, "bob": 3}

    def test_the_report_names_the_regions(self):
        left, right = diverged()
        page = report(left, right)
        assert "shared spine 5" in page
        assert "5 only left" in page
        assert "3 only right" in page
        assert "alice diverged by 5" in page

    def test_identical_tapes_report_agreement(self):
        left, _right = diverged()
        assert "identical tapes" in report(left, left)
