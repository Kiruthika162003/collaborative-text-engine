from __future__ import annotations

from loom.author import Author
from loom.blanklines import collapse_blanks
from loom.circle import Circle


class TestCollapse:
    def test_a_run_collapses_to_one_by_default(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\n\n\nb")
        collapse_blanks(author)
        assert author.text() == "a\n\nb"

    def test_the_keep_count_is_honoured(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\n\n\nb")
        collapse_blanks(author, keep=2)
        assert author.text() == "a\n\n\nb"

    def test_a_document_within_the_limit_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\nb")
        assert collapse_blanks(author, keep=1) == []


class TestFences:
    def test_blank_lines_inside_a_fence_are_spared(self):
        author = Author(site="alice")
        author.type_at(0, "```\ncode\n\n\nmore\n```")
        assert collapse_blanks(author, keep=1) == []

    def test_prose_around_a_fence_is_still_collapsed(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\n\n```\nx\n```")
        collapse_blanks(author, keep=1)
        assert author.text() == "a\n\n```\nx\n```"


class TestConvergence:
    def test_collapse_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "one\n\n\n\ntwo"),
        )
        circle.settle()
        circle.say("alice", collapse_blanks(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "one\n\ntwo"
