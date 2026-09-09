from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.setext import setext_headings, to_atx


class TestConvert:
    def test_an_equals_underline_becomes_level_one(self):
        author = Author(site="alice")
        author.type_at(0, "Title\n=====\nbody")
        to_atx(author)
        assert author.text() == "# Title\nbody"

    def test_a_dash_underline_becomes_level_two(self):
        author = Author(site="alice")
        author.type_at(0, "Sub\n---\ntext")
        to_atx(author)
        assert author.text() == "## Sub\ntext"

    def test_two_setext_headings_both_convert(self):
        author = Author(site="alice")
        author.type_at(0, "One\n===\n\nTwo\n---")
        to_atx(author)
        assert author.text() == "# One\n\n## Two"


class TestFalseFriends:
    def test_a_rule_underlining_nothing_is_left_alone(self):
        author = Author(site="alice")
        author.type_at(0, "---\nbody text")
        assert to_atx(author) == []

    def test_a_single_dash_is_not_an_underline(self):
        author = Author(site="alice")
        author.type_at(0, "Title\n-\nbody")
        assert to_atx(author) == []

    def test_setext_headings_are_detected(self):
        author = Author(site="alice")
        author.type_at(0, "H\n===")
        assert setext_headings(author) == [(0, 1)]


class TestConvergence:
    def test_conversion_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "Heading\n=======\nbody"),
        )
        circle.settle()
        circle.say("alice", to_atx(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "# Heading\nbody"
