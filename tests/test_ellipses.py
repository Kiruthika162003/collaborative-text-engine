from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.ellipses import ELLIPSIS, has_three_dots, normalize, normalized_text


class TestNormalize:
    def test_three_dots_become_an_ellipsis(self):
        author = Author(site="alice")
        author.type_at(0, "wait... really")
        normalize(author)
        assert author.text() == "wait" + ELLIPSIS + " really"

    def test_four_dots_are_left_alone(self):
        author = Author(site="alice")
        author.type_at(0, "done....")
        assert normalize(author) == []

    def test_two_dots_are_left_alone(self):
        author = Author(site="alice")
        author.type_at(0, "huh.. what")
        assert normalize(author) == []

    def test_a_hyphen_is_untouched(self):
        author = Author(site="alice")
        author.type_at(0, "a - b ... c")
        normalize(author)
        assert " - " in author.text()


class TestPure:
    def test_normalized_text_is_pure(self):
        assert normalized_text("a...b") == "a" + ELLIPSIS + "b"

    def test_has_three_dots_detects_a_run(self):
        assert has_three_dots("x...y")
        assert not has_three_dots("x..y")


class TestConvergence:
    def test_normalization_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "so... then")
        )
        circle.settle()
        circle.say("alice", normalize(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert ELLIPSIS in circle.converged()
