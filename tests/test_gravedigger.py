from __future__ import annotations

import pytest

from loom.circle import Circle
from loom.clock import VersionVector
from loom.errors import Invalid
from loom.fuzz import Storm
from loom.gravedigger import (
    Gravedigger,
    collect,
    horizon,
    quiescent,
)
from loom.snapshot import same_fabric


def settled_circle() -> Circle:
    circle = Circle.of(
        ["alice", "bob"], temperament="tides", seed=4
    )
    circle.say(
        "alice",
        circle.author("alice").type_at(0, "abcdef"),
    )
    circle.settle()
    circle.say(
        "bob", circle.author("bob").erase_at(1, 3)
    )
    circle.settle()
    return circle


class TestTheHorizon:
    def test_the_pointwise_minimum(self):
        floor = horizon(
            [
                VersionVector(
                    seen={"alice": 3, "bob": 5}
                ),
                VersionVector(
                    seen={"alice": 7, "bob": 2}
                ),
            ]
        )
        assert floor.seen == {"alice": 3, "bob": 2}

    def test_an_unseen_site_floors_at_nothing(self):
        floor = horizon(
            [
                VersionVector(seen={"alice": 3}),
                VersionVector(seen={"bob": 2}),
            ]
        )
        assert floor.seen == {}

    def test_no_clocks_is_midnight_everywhere(self):
        with pytest.raises(Invalid):
            horizon([])


class TestTheQuietRoom:
    def test_a_settled_circle_is_quiet(self):
        assert quiescent(settled_circle())

    def test_a_speaking_circle_refuses_the_digger(self):
        circle = settled_circle()
        circle.author("alice").type_at(0, "!")
        digger = Gravedigger()
        with pytest.raises(Invalid) as caught:
            digger.sweep(circle)
        assert "someone is still speaking" in str(
            caught.value
        )


class TestCollection:
    def test_graves_clear_and_origins_splice(self):
        circle = settled_circle()
        weave = circle.author("alice").weave
        assert weave.tombstone_count() == 3
        cleared, receipt = collect(weave)
        assert cleared == 3
        assert "3 grave(s) cleared" in receipt
        assert weave.tombstone_count() == 0
        assert weave.text() == "aef"

    def test_the_sweep_leaves_one_fabric(self):
        circle = settled_circle()
        digger = Gravedigger()
        report = digger.sweep(circle)
        assert "one fabric digest afterward" in report
        assert same_fabric(
            circle.author("alice").weave,
            circle.author("bob").weave,
        )

    def test_the_circle_still_converges_after_a_sweep(
        self,
    ):
        circle = settled_circle()
        Gravedigger().sweep(circle)
        storm = Storm(rounds=30, seed=11)
        storm.blow_through(circle)
        text = circle.converged()
        assert same_fabric(
            circle.author("alice").weave,
            circle.author("bob").weave,
        )
        assert isinstance(text, str)

    def test_typing_after_the_sweep_anchors_cleanly(
        self,
    ):
        circle = settled_circle()
        Gravedigger().sweep(circle)
        circle.say(
            "bob",
            circle.author("bob").type_at(1, "XY"),
        )
        circle.settle()
        assert circle.converged() == "aXYef"
