from __future__ import annotations

from loom.diffview import side_diff


class TestSideDiff:
    def test_a_changed_line_shows_old_beside_new(self):
        assert side_diff("a\nb\nc", "a\nB\nc") == "a  a\nb  B\nc  c"

    def test_context_lines_appear_on_both_sides(self):
        out = side_diff("keep\nx", "keep\ny")
        assert out.splitlines()[0] == "keep  keep"

    def test_uneven_replacement_pads_the_short_side(self):
        out = side_diff("keep\nold one\nold two\ntail", "keep\nnew\ntail")
        rows = out.splitlines()
        assert rows[1].startswith("old one")
        assert rows[2].startswith("old two")
        assert rows[3].startswith("tail")

    def test_identical_texts_show_both_columns_equal(self):
        out = side_diff("same\nlines", "same\nlines")
        for row in out.splitlines():
            halves = row.split("  ")
            assert halves[0].strip() == halves[-1].strip()
