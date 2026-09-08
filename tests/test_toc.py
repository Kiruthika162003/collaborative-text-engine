from __future__ import annotations

from loom.author import Author
from loom.toc import entries, indented, numbered


def structured() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "# Intro\n## Background\n## Goals\n# Body\n"
        "## Method\n### Detail\n# End",
    )
    return author


class TestNumbering:
    def test_numbers_follow_the_nesting(self):
        author = structured()
        page = numbered(author.weave)
        assert "1 Intro" in page
        assert "1.1 Background" in page
        assert "1.2 Goals" in page
        assert "2.1.1 Detail" in page
        assert "3 End" in page

    def test_counts_restart_under_each_parent(self):
        author = structured()
        found = {e.title: e.number for e in entries(
            author.weave
        )}
        assert found["Method"] == "2.1"

    def test_the_indented_view_shows_depth(self):
        author = structured()
        page = indented(author.weave)
        assert "    Detail" in page
        assert "  Background" in page


class TestAnchors:
    def test_an_entry_pins_to_its_heading(self):
        author = structured()
        body_pin = next(
            e.pin
            for e in entries(author.weave)
            if e.title == "Body"
        )
        author.type_at(0, "> quote\n")
        moved = next(
            e
            for e in entries(author.weave)
            if e.pin == body_pin
        )
        assert moved.title == "Body"

    def test_a_gap_is_numbered_as_it_is(self):
        author = Author(site="alice")
        author.type_at(0, "# Top\n### Deep")
        found = {
            e.title: e.number
            for e in entries(author.weave)
        }
        assert found["Top"] == "1"
        assert found["Deep"].startswith("1")

    def test_an_empty_document_has_no_contents(self):
        author = Author(site="alice")
        author.type_at(0, "just prose")
        assert "no contents" in numbered(author.weave)
