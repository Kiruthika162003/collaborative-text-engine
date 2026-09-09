from __future__ import annotations

import pytest

from loom.csvtable import CsvTable
from loom.errors import Missing

CSV = "name,age\nAl,30\nBob,5"


class TestRead:
    def test_headers_and_rows(self):
        table = CsvTable.read(CSV)
        assert table.headers == ["name", "age"]
        assert table.row_count() == 2

    def test_rows_as_dicts(self):
        table = CsvTable.read(CSV)
        assert table.dicts()[0] == {"name": "Al", "age": "30"}


class TestQuery:
    def test_a_column_by_name(self):
        assert CsvTable.read(CSV).column("age") == ["30", "5"]

    def test_select_projects_columns(self):
        projected = CsvTable.read(CSV).select("name")
        assert projected.headers == ["name"]
        assert projected.rows == [["Al"], ["Bob"]]

    def test_where_filters_rows(self):
        filtered = CsvTable.read(CSV).where(lambda r: r["name"] == "Al")
        assert filtered.rows == [["Al", "30"]]

    def test_sort_by_a_column(self):
        sorted_table = CsvTable.read(CSV).sort_by("name")
        assert sorted_table.rows[0] == ["Al", "30"]

    def test_an_unknown_column_is_refused(self):
        with pytest.raises(Missing):
            CsvTable.read(CSV).column("ghost")


class TestRender:
    def test_read_query_render_round_trips(self):
        table = CsvTable.read(CSV).select("name", "age")
        assert table.render() == CSV
