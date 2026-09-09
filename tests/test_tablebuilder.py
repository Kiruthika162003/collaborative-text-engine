from __future__ import annotations

import pytest

from loom.errors import Invalid, Missing
from loom.tablebuilder import TableBuilder


class TestBuild:
    def test_rows_are_added_and_rendered(self):
        builder = TableBuilder(["name", "age"])
        builder.add_row(["Al", "30"]).add_row(["Bob", "5"])
        rendered = builder.render()
        assert "| name | age |" in rendered
        assert "| Al" in rendered

    def test_a_short_row_is_padded(self):
        builder = TableBuilder(["a", "b", "c"])
        builder.add_row(["x"])
        assert builder.rows[0] == ["x", "", ""]

    def test_a_long_row_is_truncated(self):
        builder = TableBuilder(["a", "b"])
        builder.add_row(["1", "2", "3"])
        assert builder.rows[0] == ["1", "2"]

    def test_no_columns_is_refused(self):
        with pytest.raises(Invalid):
            TableBuilder([])


class TestColumns:
    def test_a_column_extends_every_row(self):
        builder = TableBuilder(["a"])
        builder.add_row(["1"]).add_row(["2"])
        builder.add_column("b", ["x"])
        assert builder.rows[0] == ["1", "x"]
        assert builder.rows[1] == ["2", ""]


class TestEdits:
    def test_set_cell_changes_a_value(self):
        builder = TableBuilder(["a"]).add_row(["1"])
        builder.set_cell(0, 0, "2")
        assert builder.rows[0] == ["2"]

    def test_a_bad_cell_index_is_refused(self):
        builder = TableBuilder(["a"]).add_row(["1"])
        with pytest.raises(Missing):
            builder.set_cell(9, 0, "x")

    def test_delete_row_removes_it(self):
        builder = TableBuilder(["a"]).add_row(["1"]).add_row(["2"])
        builder.delete_row(0)
        assert builder.rows == [["2"]]


class TestSort:
    def test_a_numeric_column_sorts_numerically(self):
        builder = TableBuilder(["n"]).add_row(["30"]).add_row(["5"])
        builder.sort_by(0)
        assert builder.rows == [["5"], ["30"]]

    def test_a_text_column_sorts_lexically(self):
        builder = TableBuilder(["w"]).add_row(["banana"]).add_row(["apple"])
        builder.sort_by(0)
        assert builder.rows[0] == ["apple"]


class TestCounts:
    def test_row_and_column_counts(self):
        builder = TableBuilder(["a", "b"]).add_row(["1", "2"])
        assert builder.row_count() == 1
        assert builder.column_count() == 2
