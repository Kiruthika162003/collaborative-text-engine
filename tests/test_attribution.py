from __future__ import annotations

from loom.attribution import (
    byline,
    page,
    scissors,
    shares,
)
from loom.author import Author
from loom.circle import Circle


def coauthored_circle() -> Circle:
    circle = Circle.of(["alice", "bob"])
    circle.say(
        "alice",
        circle.author("alice").type_at(0, "one two "),
    )
    circle.settle()
    circle.say(
        "bob",
        circle.author("bob").type_at(8, "three"),
    )
    circle.settle()
    return circle


class TestTheByline:
    def test_runs_fold_by_voice(self):
        circle = coauthored_circle()
        runs = byline(circle.author("alice").weave)
        assert runs == [
            ("one two ", "alice"),
            ("three", "bob"),
        ]

    def test_shares_sum_to_one_hundred(self):
        circle = coauthored_circle()
        held = shares(circle.author("bob").weave)
        assert sum(held.values()) == 100
        assert held["alice"] == 62
        assert held["bob"] == 38

    def test_the_deleted_is_decided_against(self):
        author = Author(site="alice")
        author.type_at(0, "keep CUT")
        author.erase_at(4, 4)
        held = shares(author.weave)
        assert held == {"alice": 100}
        assert byline(author.weave) == [
            ("keep", "alice")
        ]


class TestTheScissors:
    def test_erasure_is_counted_by_hand(self):
        circle = coauthored_circle()
        circle.say(
            "bob",
            circle.author("bob").erase_at(0, 4),
        )
        circle.settle()
        cut = scissors(circle.author("alice").weave)
        assert cut == {"bob": 4}


class TestThePage:
    def test_the_page_carries_all_three_censuses(self):
        circle = coauthored_circle()
        circle.say(
            "bob",
            circle.author("bob").erase_at(0, 4),
        )
        circle.settle()
        report = page(circle.author("alice").weave)
        assert "2 run(s) of voice:" in report
        assert "alice wrote" in report
        assert "bob cut 4 time(s)" in report
        assert (
            "what you deleted is what you decided "
            "against"
        ) in report

    def test_the_empty_cloth_owes_nobody(self):
        author = Author(site="alice")
        assert page(author.weave) == (
            "an empty cloth; nobody has written, "
            "nobody is owed"
        )
