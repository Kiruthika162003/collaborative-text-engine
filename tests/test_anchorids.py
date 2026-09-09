from __future__ import annotations

from loom.anchorids import add_ids, has_id
from loom.author import Author
from loom.circle import Circle


class TestAddIds:
    def test_a_heading_gets_a_slug_anchor(self):
        author = Author(site="alice")
        author.type_at(0, "# The Big Idea")
        add_ids(author)
        assert author.text() == "# The Big Idea {#the-big-idea}"

    def test_body_lines_are_untouched(self):
        author = Author(site="alice")
        author.type_at(0, "# H\nplain body")
        add_ids(author)
        assert author.text().endswith("\nplain body")

    def test_a_heading_with_an_id_is_skipped(self):
        author = Author(site="alice")
        author.type_at(0, "# Titled {#custom}")
        assert add_ids(author) == []

    def test_adding_ids_is_idempotent(self):
        author = Author(site="alice")
        author.type_at(0, "# One\n## Two")
        add_ids(author)
        assert add_ids(author) == []


class TestHasId:
    def test_has_id_detects_an_explicit_anchor(self):
        assert has_id("# Title {#slug}")
        assert not has_id("# Title")


class TestConvergence:
    def test_adding_ids_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "# My Heading")
        )
        circle.settle()
        circle.say("alice", add_ids(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "{#my-heading}" in circle.converged()
