from __future__ import annotations

from loom.pipetables import parse
from loom.tablemath import (
    column_average,
    column_extremes,
    column_sum,
    numeric_count,
    sum_from_markdown,
)

TABLE = parse("| name | age |\n| - | - |\n| Al | 30 |\n| Bob | 5 |")


class TestAggregates:
    def test_a_column_sums(self):
        assert column_sum(TABLE, 1) == 35

    def test_a_column_averages_over_numeric_cells(self):
        assert column_average(TABLE, 1) == 17.5

    def test_extremes_are_found(self):
        assert column_extremes(TABLE, 1) == (5.0, 30.0)

    def test_numeric_count_reports_how_many_counted(self):
        assert numeric_count(TABLE, 1) == 2


class TestSkipping:
    def test_non_numeric_cells_are_skipped(self):
        table = parse("| n |\n| - |\n| 10 |\n| x |\n| 20 |")
        assert column_sum(table, 0) == 30
        assert column_average(table, 0) == 15.0

    def test_a_text_column_sums_to_zero(self):
        assert column_sum(TABLE, 0) == 0.0


class TestFromMarkdown:
    def test_sum_from_markdown_parses_first(self):
        assert sum_from_markdown(
            "| n |\n| - |\n| 1 |\n| 2 |", 0
        ) == 3
