from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.wrapwide import fits_display, wrap_display


class TestWrap:
    def test_latin_wraps_greedily(self):
        assert wrap_display("aa bb cc", 5) == "aa bb\ncc"

    def test_wide_glyphs_wrap_by_cell(self):
        assert wrap_display("中文 x", 4) == "中文\nx"

    def test_a_long_word_sits_alone(self):
        assert wrap_display("supercali x", 5) == "supercali\nx"

    def test_blank_lines_between_paragraphs_survive(self):
        assert wrap_display("a b\n\nc d", 80) == "a b\n\nc d"

    def test_a_zero_width_is_refused(self):
        with pytest.raises(Invalid):
            wrap_display("x", 0)


class TestFits:
    def test_a_wrapped_paragraph_fits_by_display_width(self):
        wrapped = wrap_display("中文 中文 中文", 4)
        assert fits_display(wrapped, 4)

    def test_an_overlong_line_does_not_fit(self):
        assert not fits_display("中文中文", 3)
