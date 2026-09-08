from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Missing
from loom.linewise import (
    erase_at_line,
    line_count,
    line_of,
    line_text,
    type_at_line,
    visible_index,
)


def three_lines() -> Author:
    author = Author(site="alice")
    author.type_at(0, "one\ntwo\nthree")
    return author


class TestReadingLines:
    def test_lines_are_what_newlines_make_them(self):
        author = three_lines()
        assert line_count(author.weave) == 3
        assert line_text(author.weave, 1) == "two"

    def test_refusals_teach_the_territory(self):
        author = three_lines()
        with pytest.raises(Missing) as caught:
            line_text(author.weave, 9)
        assert "of a 3-line cloth" in str(caught.value)

    def test_a_dead_newline_divides_nothing(self):
        author = three_lines()
        author.erase_at(3, 1)
        assert line_count(author.weave) == 2
        assert line_text(author.weave, 0) == "onetwo"


class TestTranslation:
    def test_two_numbers_become_one_index(self):
        author = three_lines()
        assert visible_index(author.weave, 0, 0) == 0
        assert visible_index(author.weave, 1, 2) == 6
        assert visible_index(author.weave, 2, 5) == 13

    def test_a_column_past_the_line_is_refused(self):
        author = three_lines()
        with pytest.raises(Missing) as caught:
            visible_index(author.weave, 1, 9)
        assert "line of 3 glyph(s)" in str(caught.value)

    def test_a_strand_knows_its_current_line(self):
        author = three_lines()
        strand = author.weave.strand_at_visible(8)
        assert strand.glyph == "t"
        assert line_of(author.weave, strand.id) == 2
        author.erase_at(3, 1)
        assert line_of(author.weave, strand.id) == 1


class TestHumanGestures:
    def test_typing_speaks_line_and_column(self):
        author = three_lines()
        type_at_line(author, 1, 3, " more")
        assert line_text(author.weave, 1) == "two more"

    def test_erasing_speaks_line_and_column(self):
        author = three_lines()
        erase_at_line(author, 2, 0, 3)
        assert line_text(author.weave, 2) == "ee"
