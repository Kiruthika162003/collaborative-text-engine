from __future__ import annotations

from loom.author import Author
from loom.captions import captions, list_of, of_kind, report


def illustrated() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "Figure: the river\nsome prose\nTable: the results\n"
        "Figure: the map\nmore prose",
    )
    return author


class TestNumbering:
    def test_figures_and_tables_count_apart(self):
        found = {c.label() for c in captions(illustrated().weave)}
        assert "Figure 1" in found
        assert "Figure 2" in found
        assert "Table 1" in found

    def test_numbers_follow_reading_order(self):
        figures = of_kind(illustrated().weave, "Figure")
        assert figures[0].text == "the river"
        assert figures[1].text == "the map"

    def test_inserting_a_figure_renumbers(self):
        author = illustrated().weave
        pins = {c.text: c.number for c in of_kind(author, "Figure")}
        assert pins["the map"] == 2


class TestLists:
    def test_the_list_of_figures_renders(self):
        page = list_of(illustrated().weave, "Figure")
        assert "Figure 1: the river" in page
        assert "Figure 2: the map" in page

    def test_a_kind_with_none_says_so(self):
        assert "no listings" in list_of(illustrated().weave, "Listing")


class TestPin:
    def test_a_caption_pins_to_its_line(self):
        author = illustrated()
        pin = of_kind(author.weave, "Table")[0].pin
        author.type_at(0, "PREFIX\n")
        moved = of_kind(author.weave, "Table")[0]
        assert moved.pin == pin
        assert moved.text == "the results"


class TestReport:
    def test_the_report_counts_by_kind(self):
        page = report(illustrated().weave)
        assert "3 caption(s)" in page
        assert "2 figure(s)" in page
        assert "1 table(s)" in page

    def test_a_plain_document_has_no_captions(self):
        author = Author(site="alice")
        author.type_at(0, "just prose")
        assert "no figures or tables" in report(author.weave)
