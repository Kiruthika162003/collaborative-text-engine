from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Missing
from loom.mailroom import Mailroom
from loom.snapshot import same_fabric
from loom.transcript import Tape


def taped_author() -> tuple[Author, Tape]:
    tape = Tape()
    author = Author(site="alice", tape=tape)
    author.type_at(0, "recorded")
    author.erase_at(0, 3)
    author.type_at(0, "un")
    return author, tape


class TestTestimony:
    def test_the_replay_matches_the_living_fabric(self):
        author, tape = taped_author()
        assert author.text() == "unorded"
        assert tape.testifies_for(author.weave)
        assert tape.length() == 13

    def test_remote_weaving_is_taped_too(self):
        tape = Tape()
        bob = Author(site="bob", tape=tape)
        mailroom = Mailroom(author=bob)
        alice = Author(site="alice")
        ops = alice.type_at(0, "abc")
        for op in reversed(ops):
            mailroom.receive(op)
        assert tape.length() == 3
        assert tape.testifies_for(bob.weave)

    def test_the_tape_travels_and_still_testifies(self):
        author, tape = taped_author()
        loaded = Tape.load(tape.dump())
        assert loaded.length() == tape.length()
        assert loaded.testifies_for(author.weave)

    def test_a_shuffled_tape_refuses_to_play(self):
        _author, tape = taped_author()
        backwards = Tape(
            reel=list(reversed(tape.reel))
        )
        with pytest.raises(Missing):
            backwards.replay()

    def test_the_tape_records_weave_order_not_arrival(
        self,
    ):
        tape = Tape()
        bob = Author(site="bob", tape=tape)
        mailroom = Mailroom(author=bob)
        alice = Author(site="alice")
        ops = alice.type_at(0, "xy")
        mailroom.receive(ops[1])
        mailroom.receive(ops[0])
        assert [op.id.counter for op in tape.reel] == [
            1,
            2,
        ]


class TestCircleTestimony:
    def test_every_seat_can_be_audited(self):
        tapes = {}
        circle = Circle.of(
            ["alice", "bob"],
            temperament="gremlin",
            seed=13,
        )
        for site, author in circle.authors.items():
            tapes[site] = Tape()
            author.tape = tapes[site]
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "abc"),
        )
        circle.say(
            "bob",
            circle.author("bob").type_at(0, "xyz"),
        )
        circle.settle()
        circle.converged()
        for site, author in circle.authors.items():
            assert tapes[site].testifies_for(
                author.weave
            )
        assert same_fabric(
            tapes["alice"].replay(),
            tapes["bob"].replay(),
        )
