"""Table math: sum and average a numeric column of a Markdown table.

A table of numbers invites arithmetic, and this does the
column aggregations a reader asks of one: the sum, the
average, and the extremes of a chosen column. It reads the
column's cells and keeps the ones that parse as numbers,
skipping the rest, which is the honest way to handle a column
that is mostly numeric with a stray blank or a footnote
marker: those cells contribute nothing rather than crashing
the sum, and the count of numeric cells is available so a
caller can see how many of the rows actually counted. The
average is over the numeric cells only, not the row count, so
a column with two numbers and a blank averages the two rather
than dividing by three and understating it, which is what
average means when some cells are not numbers. It works on a
parsed table so the same aggregation serves a caller who
already has one and a caller starting from Markdown text
through the convenience that parses first, and it computes
over the data rows, never the header, since a header is a
label and summing it is a category error a looser reader would
make. A column with no numbers sums to zero and averages to
zero rather than raising, because a table can legitimately
have a text column and asking its sum is a question with a
plain answer, not an error.
"""

from __future__ import annotations

from loom.pipetables import Table, parse


def _column_cells(table: Table, index: int) -> list[str]:
    return [
        row[index] if index < len(row) else "" for row in table.rows
    ]


def _numbers(cells: list[str]) -> list[float]:
    values = []
    for cell in cells:
        try:
            values.append(float(cell))
        except ValueError:
            continue
    return values


def numeric_count(table: Table, index: int) -> int:
    return len(_numbers(_column_cells(table, index)))


def column_sum(table: Table, index: int) -> float:
    return sum(_numbers(_column_cells(table, index)))


def column_average(table: Table, index: int) -> float:
    values = _numbers(_column_cells(table, index))
    return sum(values) / len(values) if values else 0.0


def column_extremes(table: Table, index: int) -> tuple[float, float]:
    values = _numbers(_column_cells(table, index))
    if not values:
        return (0.0, 0.0)
    return (min(values), max(values))


def sum_from_markdown(text: str, index: int) -> float:
    table = parse(text)
    return column_sum(table, index) if table is not None else 0.0
