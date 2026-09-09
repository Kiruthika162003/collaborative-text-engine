from __future__ import annotations

from loom.author import Author
from loom.sectionstats import (
    report,
    section_words,
    thin_sections,
    total_words,
)


def documented() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "intro words here\n# One\nbody of one two three\n# Two\nshort",
    )
    return author


class TestSectionWords:
    def test_each_section_is_counted(self):
        sections = section_words(documented().weave)
        found = {s.title: s.words for s in sections}
        assert found["(preamble)"] == 3
        assert found["One"] == 5
        assert found["Two"] == 1

    def test_a_heading_line_is_not_counted_in_its_body(self):
        author = Author(site="alice")
        author.type_at(0, "# A long heading title here\nword")
        section = next(
            s for s in section_words(author.weave) if s.title.startswith("A")
        )
        assert section.words == 1

    def test_an_empty_preamble_is_dropped(self):
        author = Author(site="alice")
        author.type_at(0, "# Start\nbody")
        titles = [s.title for s in section_words(author.weave)]
        assert "(preamble)" not in titles


class TestQueries:
    def test_thin_sections_are_flagged(self):
        thin = thin_sections(documented().weave, threshold=2)
        assert [s.title for s in thin] == ["Two"]

    def test_total_words_sums_the_sections(self):
        assert total_words(documented().weave) == 9


class TestReport:
    def test_the_report_lists_sections(self):
        page = report(documented().weave)
        assert "One: 5 word(s)" in page
        assert "not verdicts" in page

    def test_an_empty_document_reports_nothing(self):
        author = Author(site="alice")
        assert "no sections" in report(author.weave)
