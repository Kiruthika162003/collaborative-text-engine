from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.courier import Link
from loom.errors import Diverged, Invalid, Missing
from loom.mailroom import Mailroom


class TestTheLink:
    def test_calm_delivers_in_order(self):
        alice = Author(site="alice")
        bob = Author(site="bob")
        link = Link(to=Mailroom(author=bob))
        link.post_many(alice.type_at(0, "hello"))
        link.deliver_batch()
        assert bob.text() == "hello"
        assert "5 posted, 5 delivered" in link.ledger()

    def test_tides_shuffle_but_the_weave_shrugs(self):
        alice = Author(site="alice")
        bob = Author(site="bob")
        link = Link(
            to=Mailroom(author=bob),
            temperament="tides",
            seed=11,
        )
        link.post_many(
            alice.type_at(0, "the tide came in")
        )
        link.deliver_batch()
        assert bob.text() == "the tide came in"

    def test_the_gremlin_bills_its_duplicates(self):
        alice = Author(site="alice")
        bob = Author(site="bob")
        room = Mailroom(author=bob)
        link = Link(
            to=room, temperament="gremlin", seed=3
        )
        link.post_many(alice.type_at(0, "gremlins!"))
        link.deliver_batch()
        assert bob.text() == "gremlins!"
        assert link.duplicated == 3
        assert room.duplicates == 3

    def test_temperaments_are_a_closed_set(self):
        bob = Author(site="bob")
        with pytest.raises(Invalid):
            Link(
                to=Mailroom(author=bob),
                temperament="hurricane",
            )


class TestTheCircle:
    def test_say_settle_converge(self):
        circle = Circle.of(["alice", "bob", "cara"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "hi "),
        )
        circle.settle()
        circle.say(
            "bob",
            circle.author("bob").type_at(3, "there"),
        )
        report = circle.settle()
        assert "0 arrival(s) still shelved" in report
        assert circle.converged() == "hi there"

    def test_divergence_is_an_alarm_not_a_summary(self):
        circle = Circle.of(["alice", "bob"])
        circle.author("alice").type_at(0, "mine")
        with pytest.raises(Diverged) as caught:
            circle.converged()
        message = str(caught.value)
        assert "alice reads 'mine'" in message
        assert "bob reads ''" in message

    def test_a_circle_of_one_is_a_diary(self):
        with pytest.raises(Invalid):
            Circle.of(["alice"])

    def test_a_stranger_is_not_seated(self):
        circle = Circle.of(["alice", "bob"])
        with pytest.raises(Missing):
            circle.author("mallory")

    def test_gremlin_circles_still_converge(self):
        circle = Circle.of(
            ["alice", "bob", "cara"],
            temperament="gremlin",
            seed=42,
        )
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "abc"),
        )
        circle.say(
            "bob",
            circle.author("bob").type_at(0, "xyz"),
        )
        circle.settle()
        text = circle.converged()
        assert text in ("abcxyz", "xyzabc")
        assert "duplicate(s) manufactured" in (
            circle.mischief_bill()
        )
