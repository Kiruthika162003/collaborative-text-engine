from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.titlecase import retitle, title_case


class TestTitleCase:
    def test_small_words_stay_lowercase_mid_title(self):
        assert title_case("the lord of the rings") == "The Lord of the Rings"

    def test_the_first_word_is_capitalized_even_if_small(self):
        assert title_case("a tale of two cities") == "A Tale of Two Cities"

    def test_the_last_word_is_capitalized_even_if_small(self):
        assert title_case("what is it for") == "What Is It For"

    def test_an_acronym_is_preserved(self):
        assert title_case("the NASA report") == "The NASA Report"

    def test_an_empty_title_is_unchanged(self):
        assert title_case("") == ""


class TestRetitle:
    def test_a_heading_is_title_cased_keeping_its_marker(self):
        author = Author(site="alice")
        author.type_at(0, "## the art of war")
        retitle(author, 0)
        assert author.text() == "## The Art of War"

    def test_a_plain_line_is_title_cased(self):
        author = Author(site="alice")
        author.type_at(0, "a study in scarlet")
        retitle(author, 0)
        assert author.text() == "A Study in Scarlet"


class TestConvergence:
    def test_retitle_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "# the sound and the fury"),
        )
        circle.settle()
        circle.say("alice", retitle(circle.author("alice"), 0))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "# The Sound and the Fury"
