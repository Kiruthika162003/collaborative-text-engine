from __future__ import annotations

import pytest

from loom.coords import display_column, linecol_to_offset, offset_to_linecol
from loom.errors import Invalid, Missing

TEXT = "one\ntwo\nthree"


class TestOffsetToLineCol:
    def test_the_first_line(self):
        assert offset_to_linecol(TEXT, 1) == (0, 1)

    def test_a_later_line(self):
        assert offset_to_linecol(TEXT, 4) == (1, 0)

    def test_the_very_end(self):
        assert offset_to_linecol(TEXT, len(TEXT)) == (2, 5)

    def test_an_out_of_range_offset_is_refused(self):
        with pytest.raises(Invalid):
            offset_to_linecol(TEXT, 99)


class TestLineColToOffset:
    def test_a_coordinate_becomes_an_offset(self):
        assert linecol_to_offset(TEXT, 1, 0) == 4

    def test_a_bad_line_is_refused(self):
        with pytest.raises(Missing):
            linecol_to_offset(TEXT, 9, 0)

    def test_a_bad_column_is_refused(self):
        with pytest.raises(Missing):
            linecol_to_offset(TEXT, 0, 99)


class TestRoundTrip:
    def test_offset_survives_a_round_trip(self):
        for offset in range(len(TEXT) + 1):
            line, column = offset_to_linecol(TEXT, offset)
            assert linecol_to_offset(TEXT, line, column) == offset


class TestDisplay:
    def test_a_tab_advances_the_display_column(self):
        assert display_column("a\tb", 2, tab=4) == 4

    def test_a_wide_glyph_advances_two(self):
        assert display_column("中x", 1) == 2
