from __future__ import annotations

import pytest

from loom.author import Author
from loom.confluence import (
    confluence,
    contributed_glyphs,
    glyph_authors,
    joined_text,
    op_union_size,
)
from loom.errors import Missing
from loom.mailroom import Mailroom
from loom.snapshot import fabric_digest, same_fabric
from loom.transcript import Tape


def divergent_tapes() -> tuple[Tape, Tape]:
    shared_tape = Tape()
    alice = Author(site="alice", tape=shared_tape)
    ops = alice.type_at(0, "shared ")

    bob = Author(site="bob")
    bob_room = Mailroom(author=bob)
    bob.tape = Tape()
    for op in ops:
        bob_room.receive(op)
    left = alice.tape
    alice.type_at(7, "alice")
    bob.type_at(7, "bob")
    return left, bob.tape


class TestJoining:
    def test_operations_join_where_text_could_not(self):
        left, right = divergent_tapes()
        joined = joined_text(left, right)
        assert "shared" in joined
        assert "alice" in joined
        assert "bob" in joined

    def test_join_matches_a_handshake(self):
        left, right = divergent_tapes()
        joined = confluence(left, right)
        arrival = Author(site="cara")
        room = Mailroom(author=arrival)
        for op in list(right.reel) + list(left.reel):
            room.receive(op)
        assert same_fabric(joined, arrival.weave)
        assert fabric_digest(joined) == fabric_digest(
            arrival.weave
        )

    def test_the_join_is_order_independent(self):
        left, right = divergent_tapes()
        one = confluence(left, right)
        two = confluence(right, left)
        assert same_fabric(one, two)

    def test_the_union_counts_each_op_once(self):
        left, right = divergent_tapes()
        assert op_union_size(left, right) == 15


class TestStrangers:
    def test_two_head_rooted_drafts_do_join(self):
        alice = Author(site="alice", tape=Tape())
        alice.type_at(0, "one")
        other = Author(site="bob", tape=Tape())
        other.type_at(0, "two")
        joined = joined_text(alice.tape, other.tape)
        assert "one" in joined
        assert "two" in joined

    def test_a_truncated_tape_is_refused(self):
        author = Author(site="alice", tape=Tape())
        ops = author.type_at(0, "abcd")
        fragment = Tape(reel=list(ops[2:]))
        with pytest.raises(Missing) as caught:
            confluence(Tape(), fragment)
        assert "neither document" in str(caught.value)


class TestCensus:
    def test_glyph_authors_split_the_join(self):
        left, right = divergent_tapes()
        counts = glyph_authors(left, right)
        assert counts["alice"] == 12
        assert counts["bob"] == 3

    def test_a_tape_reports_its_contribution(self):
        left, _right = divergent_tapes()
        assert contributed_glyphs(left) == 12
