from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.headingtitles import titlecase_headings


class TestTitlecaseHeadings:
    def test_all_headings_are_title_cased(self):
        author = Author(site="alice")
        author.type_at(0, "# the big idea\nbody\n## a small note")
        titlecase_headings(author)
        assert author.text() == (
            "# The Big Idea\nbody\n## A Small Note"
        )

    def test_body_lines_are_untouched(self):
        author = Author(site="alice")
        author.type_at(0, "# heading\nthe body stays lower")
        titlecase_headings(author)
        assert author.text().endswith("the body stays lower")

    def test_an_already_titled_document_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "# The Big Idea")
        assert titlecase_headings(author) == []

    def test_it_is_idempotent(self):
        author = Author(site="alice")
        author.type_at(0, "# the sound and the fury")
        titlecase_headings(author)
        assert titlecase_headings(author) == []


class TestConvergence:
    def test_titlecasing_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "# a tale of two")
        )
        circle.settle()
        circle.say("alice", titlecase_headings(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "# A Tale of Two"
