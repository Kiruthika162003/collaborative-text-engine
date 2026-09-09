from __future__ import annotations

from loom.columns import display_width
from loom.sidebyside import side_by_side


class TestSideBySide:
    def test_two_blocks_sit_in_columns(self):
        assert side_by_side(["a\nbb", "x\ny"]) == "a   x\nbb  y"

    def test_a_shorter_block_is_padded_below(self):
        out = side_by_side(["a\nb\nc", "x"])
        assert out == "a  x\nb\nc"

    def test_a_single_block_is_itself(self):
        assert side_by_side(["a\nb"]) == "a\nb"

    def test_no_blocks_is_empty(self):
        assert side_by_side([]) == ""


class TestAlignment:
    def test_columns_start_at_a_straight_edge(self):
        out = side_by_side(["short\nlonger line", "x\ny"])
        rows = out.splitlines()
        # the second column starts at the same offset on every row
        starts = [row.index("x") if "x" in row else row.index("y") for row in rows]
        assert len(set(starts)) == 1

    def test_a_wide_glyph_keeps_the_column_aligned(self):
        out = side_by_side(["中\nxx", "a\nb"])
        rows = out.splitlines()
        first_col_widths = {display_width(row.split("  ")[0]) for row in rows}
        assert len(first_col_widths) == 1
