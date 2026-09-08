from __future__ import annotations

import pytest

from loom.columns import (
    display_width,
    glyph_at_column,
    glyph_width,
    is_wide,
    pad_to,
    visual_column,
)
from loom.errors import Invalid


class TestGlyphWidth:
    def test_a_latin_glyph_takes_one_cell(self):
        assert glyph_width("a") == 1

    def test_a_wide_glyph_takes_two_cells(self):
        assert glyph_width("中") == 2

    def test_a_combining_mark_takes_none(self):
        assert glyph_width("́") == 0

    def test_a_tab_jumps_to_the_next_stop(self):
        assert glyph_width("\t", column=0, tab=4) == 4
        assert glyph_width("\t", column=1, tab=4) == 3

    def test_a_tab_of_zero_width_is_refused(self):
        with pytest.raises(Invalid):
            glyph_width("\t", tab=0)


class TestDisplayWidth:
    def test_latin_width_equals_length(self):
        assert display_width("hello") == 5

    def test_wide_glyphs_double_the_width(self):
        text = "中文"
        assert display_width(text) == 4

    def test_a_combined_letter_and_mark_is_one_cell(self):
        text = "é"
        assert display_width(text) == 1


class TestVisualColumn:
    def test_a_caret_past_a_wide_glyph_sits_at_two(self):
        assert visual_column("中x", 1) == 2

    def test_a_caret_out_of_range_is_refused(self):
        with pytest.raises(Invalid):
            visual_column("abc", 9)


class TestGlyphAtColumn:
    def test_a_column_lands_on_the_glyph_after_a_wide_one(self):
        assert glyph_at_column("中x", 2) == 1

    def test_a_column_inside_a_wide_glyph_stops_before_it(self):
        assert glyph_at_column("中x", 1) == 0

    def test_a_negative_column_is_refused(self):
        with pytest.raises(Invalid):
            glyph_at_column("abc", -1)


class TestPadding:
    def test_padding_counts_visual_width_not_glyphs(self):
        assert pad_to("中", 4) == "中  "

    def test_padding_leaves_wide_enough_text_alone(self):
        assert pad_to("hello", 3) == "hello"


class TestIsWide:
    def test_a_wide_glyph_reports_wide(self):
        assert is_wide("中")

    def test_a_latin_glyph_is_not_wide(self):
        assert not is_wide("a")
