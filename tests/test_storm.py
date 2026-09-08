from __future__ import annotations

import random

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid
from loom.fuzz import Storm, gust
from loom.trials.stormtrial import run


class TestGusts:
    def test_gusts_never_break_physics(self):
        author = Author(site="solo")
        dice = random.Random(3)
        for _ in range(200):
            gust(author, dice)
        assert author.weave.visible_count() == len(
            author.text()
        )

    def test_the_first_gust_types(self):
        author = Author(site="solo")
        ops = gust(author, random.Random(1))
        assert all(hasattr(op, "glyph") for op in ops)

    def test_a_storm_of_zero_rounds_is_a_forecast(self):
        circle = Circle.of(["alice", "bob"])
        with pytest.raises(Invalid):
            Storm(rounds=0, seed=1).blow_through(circle)

    def test_the_same_seed_blows_the_same_storm(self):
        bills = []
        for _attempt in range(2):
            circle = Circle.of(
                ["alice", "bob"],
                temperament="tides",
                seed=5,
            )
            storm = Storm(rounds=30, seed=5)
            storm.blow_through(circle)
            bills.append(
                (storm.typed, storm.erased,
                 circle.converged())
            )
        assert bills[0] == bills[1]


class TestTheStormTrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_gestures_and_victims_part_ways(self):
        verdict = run()
        assert verdict.numbers["erased_gestures"] == 66
        assert verdict.numbers["victims"] == 56
        assert verdict.numbers["double_cuts"] == 10

    def test_the_honest_equation_holds_to_the_glyph(
        self,
    ):
        verdict = run()
        assert verdict.numbers["arithmetic_holds"]
        assert verdict.numbers["final_length"] == 88

    def test_the_gremlins_billed_and_changed_nothing(
        self,
    ):
        verdict = run()
        assert (
            verdict.numbers["duplicates_manufactured"]
            == 147
        )
