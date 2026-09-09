from __future__ import annotations

from loom.boxes import box
from loom.columns import display_width


class TestBox:
    def test_a_single_line_is_framed(self):
        assert box("hi") == "+----+\n| hi |\n+----+"

    def test_multi_line_text_is_a_rectangle(self):
        framed = box("a\nbb").splitlines()
        widths = {len(line) for line in framed}
        assert len(widths) == 1

    def test_padding_is_honoured(self):
        framed = box("x", padding=2)
        assert framed.splitlines()[1] == "|  x  |"

    def test_zero_padding_hugs_the_text(self):
        assert box("hi", padding=0) == "+--+\n|hi|\n+--+"


class TestWidth:
    def test_a_wide_glyph_box_aligns(self):
        framed = box("中\nx").splitlines()
        widths = {display_width(line) for line in framed}
        assert len(widths) == 1

    def test_the_box_fits_the_widest_line(self):
        framed = box("short\nmuch longer line")
        top = framed.splitlines()[0]
        assert len(top) == display_width("much longer line") + 4
