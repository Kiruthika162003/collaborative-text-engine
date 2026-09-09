from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.sectionnumbers import (
    number_headings,
    preview,
    strip_numbers,
)


def outlined() -> Author:
    author = Author(site="alice")
    author.type_at(0, "# Intro\n## Background\n## Goals\n# Body\ntext")
    return author


class TestNumber:
    def test_numbers_are_written_into_the_headings(self):
        author = outlined()
        number_headings(author)
        assert author.text() == (
            "# 1 Intro\n## 1.1 Background\n## 1.2 Goals\n# 2 Body\ntext"
        )

    def test_prose_lines_are_untouched(self):
        author = outlined()
        number_headings(author)
        assert author.text().endswith("\ntext")

    def test_numbering_is_idempotent(self):
        author = outlined()
        number_headings(author)
        assert number_headings(author) == []


class TestStrip:
    def test_stripping_removes_the_numbers(self):
        author = outlined()
        number_headings(author)
        strip_numbers(author)
        assert author.text() == (
            "# Intro\n## Background\n## Goals\n# Body\ntext"
        )

    def test_a_deep_heading_with_a_bare_number_keeps_it(self):
        # a subsection's number is always dotted, so a bare
        # year at depth two is not mistaken for one
        author = Author(site="alice")
        author.type_at(0, "# Top\n## 2024 in review")
        strip_numbers(author)
        assert author.text() == "# Top\n## 2024 in review"


class TestPreview:
    def test_preview_shows_numbers_without_editing(self):
        author = outlined()
        page = preview(author.weave)
        assert "1.1 Background" in page
        assert author.text() == (
            "# Intro\n## Background\n## Goals\n# Body\ntext"
        )

    def test_a_flat_document_has_nothing_to_number(self):
        author = Author(site="alice")
        author.type_at(0, "no headings")
        assert "no headings to number" in preview(author.weave)


class TestConvergence:
    def test_numbering_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "# One\n## Two"),
        )
        circle.settle()
        circle.say("alice", number_headings(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "# 1 One" in circle.converged()
