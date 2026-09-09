from __future__ import annotations

from loom.rectangle import column, drop_columns, slice_columns, widest


class TestSlice:
    def test_a_column_range_is_sliced_from_each_line(self):
        assert slice_columns("abcd\nefgh\nijkl", 1, 3) == "bc\nfg\njk"

    def test_a_short_line_contributes_what_it_has(self):
        assert slice_columns("abcd\nef", 1, 3) == "bc\nf"


class TestDrop:
    def test_a_column_range_is_removed(self):
        assert drop_columns("abcd\nefgh\nijkl", 1, 3) == "ad\neh\nil"

    def test_dropping_past_a_short_line_leaves_its_head(self):
        assert drop_columns("abcd\nef", 1, 3) == "ad\ne"


class TestColumn:
    def test_a_single_column_reads_down(self):
        assert column("abc\ndef\nghi", 0) == "adg"

    def test_a_short_line_is_skipped_for_that_column(self):
        assert column("abc\nd\nghi", 2) == "ci"


class TestWidest:
    def test_widest_is_the_longest_line(self):
        assert widest("a\nbbb\ncc") == 3
