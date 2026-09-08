from __future__ import annotations

from loom.author import Author
from loom.census import (
    hands_seen,
    high_water_rank,
    longest_single_hand_run,
    page,
)
from loom.circle import Circle


def negotiated_circle() -> Circle:
    circle = Circle.of(["alice", "bob"])
    circle.say(
        "alice",
        circle.author("alice").type_at(0, "aaaa"),
    )
    circle.settle()
    circle.say(
        "bob", circle.author("bob").type_at(2, "bb")
    )
    circle.settle()
    return circle


class TestTheNumbers:
    def test_runs_measure_negotiation(self):
        circle = negotiated_circle()
        weave = circle.author("alice").weave
        assert longest_single_hand_run(weave) == 2

    def test_a_diary_has_one_long_run(self):
        author = Author(site="alice")
        author.type_at(0, "monologue")
        assert (
            longest_single_hand_run(author.weave) == 9
        )

    def test_shearing_hands_are_hands_too(self):
        author = Author(site="alice")
        ops = author.type_at(0, "ab")
        cutter = Author(site="bob")
        for op in ops:
            cutter.absorb(op)
        for op in cutter.erase_at(0, 1):
            author.absorb(op)
        assert hands_seen(author.weave) == [
            "alice",
            "bob",
        ]

    def test_high_water_follows_the_witnessing(self):
        circle = negotiated_circle()
        assert (
            high_water_rank(
                circle.author("bob").weave
            )
            == 6
        )


class TestThePage:
    def test_the_page_counts_without_nagging(self):
        circle = negotiated_circle()
        report = page(circle.author("alice").weave)
        assert "6 strand(s), 6 showing, 0 dead" in (
            report
        )
        assert "2 hand(s) ever touched" in report
        assert "longest single-hand run 2" in report
        assert "census that nags" in report
        assert "past the 40% line" not in report

    def test_heavy_history_is_stated_not_scolded(self):
        author = Author(site="alice")
        author.type_at(0, "abcde")
        author.erase_at(0, 3)
        report = page(author.weave)
        assert "3 dead (60%)" in report
        assert (
            "wears more history than text"
        ) in report

    def test_the_unwoven_fabric_is_all_future(self):
        author = Author(site="alice")
        assert "every future is open" in page(
            author.weave
        )
