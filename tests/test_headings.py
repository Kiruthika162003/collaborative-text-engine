from __future__ import annotations

from loom.author import Author
from loom.headings import (
    depth,
    headings,
    level_counts,
    outline,
)


def structured() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "# Title\nintro\n## Section A\ntext\n"
        "### Deep\nmore\n## Section B",
    )
    return author


class TestReadingHeadings:
    def test_hash_marks_become_levels(self):
        author = structured()
        found = headings(author.weave)
        assert [h.level for h in found] == [1, 2, 3, 2]
        assert found[0].title == "Title"

    def test_the_outline_nests_by_level(self):
        author = structured()
        page = outline(author.weave)
        assert "Title" in page
        assert "  Section A" in page
        assert "    Deep" in page

    def test_a_flat_document_has_no_headings(self):
        author = Author(site="alice")
        author.type_at(0, "just prose here")
        assert "the document is flat" in outline(
            author.weave
        )

    def test_a_bare_hash_is_not_a_heading(self):
        author = Author(site="alice")
        author.type_at(0, "#nospace\ntext")
        assert headings(author.weave) == []


class TestGapsAndNumbers:
    def test_a_skipped_level_is_flagged(self):
        author = Author(site="alice")
        author.type_at(0, "# Top\n### Skipped")
        page = outline(author.weave)
        assert "level gap" in page

    def test_depth_and_counts_are_reported(self):
        author = structured()
        assert depth(author.weave) == 3
        assert level_counts(author.weave) == {
            1: 1,
            2: 2,
            3: 1,
        }

    def test_a_pin_survives_the_section_moving(self):
        author = structured()
        section_pin = headings(author.weave)[1].pin
        author.type_at(0, "> quote\n")
        moved = next(
            h
            for h in headings(author.weave)
            if h.pin == section_pin
        )
        assert moved.title == "Section A"
