from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.pages import (
    page_count,
    page_of_line,
    page_of_strand,
    paginate,
    render,
)


def five_lines() -> Author:
    author = Author(site="alice")
    author.type_at(0, "one\ntwo\nthree\nfour\nfive")
    return author


class TestPaginate:
    def test_lines_are_cut_into_pages_of_the_budget(self):
        pages = paginate(five_lines().weave, 2)
        assert len(pages) == 3
        assert pages[0].lines == ["one", "two"]
        assert pages[2].lines == ["five"]

    def test_a_page_pins_to_its_first_glyph(self):
        author = five_lines()
        pages = paginate(author.weave, 2)
        second = pages[1].start_pin
        assert author.weave.strands[
            author.weave.by_id[second]
        ].glyph == "t"

    def test_a_blank_first_line_pins_to_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "\nbody")
        pages = paginate(author.weave, 1)
        assert pages[0].start_pin is None


class TestCounts:
    def test_page_count_rounds_up(self):
        assert page_count(five_lines().weave, 2) == 3

    def test_an_empty_document_is_one_page(self):
        author = Author(site="alice")
        assert page_count(author.weave, 10) == 1

    def test_a_zero_budget_is_refused(self):
        with pytest.raises(Invalid):
            page_count(five_lines().weave, 0)


class TestLocate:
    def test_a_line_reports_its_page(self):
        weave = five_lines().weave
        assert page_of_line(weave, 0, 2) == 1
        assert page_of_line(weave, 2, 2) == 2
        assert page_of_line(weave, 4, 2) == 3

    def test_a_line_out_of_range_is_refused(self):
        with pytest.raises(Missing):
            page_of_line(five_lines().weave, 9, 2)


class TestPin:
    def test_a_pin_moves_page_when_lines_are_added_above(self):
        author = five_lines()
        pages = paginate(author.weave, 2)
        fifth_pin = pages[2].start_pin
        assert page_of_strand(author.weave, fifth_pin, 2) == 3
        author.type_at(0, "zero\n")
        assert page_of_strand(author.weave, fifth_pin, 2) == 3
        author.type_at(0, "again\n")
        assert page_of_strand(author.weave, fifth_pin, 2) == 4


class TestRender:
    def test_render_labels_each_page(self):
        page = render(five_lines().weave, 2)
        assert "[page 1 of 3]" in page
        assert "[page 3 of 3]" in page
