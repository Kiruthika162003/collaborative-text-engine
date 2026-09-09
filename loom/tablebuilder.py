"""Table builder: build a Markdown table in memory by adding rows and columns.

The pipe-tables module parses and renders a table, and the
grid module holds one as a convergent CRDT; this is the third
thing a caller wants, a plain mutable builder for assembling a
table before it becomes text, with the fluent add-row,
add-column, set-cell, delete-row, and sort operations a caller
reaches for when producing a table from data. Every operation
keeps the table rectangular, which is the invariant a builder
must never break: a row added with fewer cells than there are
columns is padded with empties, one with more is truncated to
the column count, and adding a column extends every existing
row so no row is left short a cell. The mutating methods
return the builder so calls chain, add a row then another then
sort in one expression, which reads the way building a table
reads. Indices are validated and an out-of-range row or column
is refused with the table's actual shape named, because a
builder that silently ignored a bad index would leave a caller
believing an edit happened that did not. When the table is
ready it converts to the pipe-tables structure and renders
through that module's renderer, so a built table aligns and
reads exactly like a parsed one, and the two modules share one
notion of what a rendered table looks like rather than each
having its own.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid, Missing
from loom.pipetables import Table
from loom.pipetables import render as render_table


@dataclass
class TableBuilder:
    headers: list[str]
    alignments: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.headers:
            raise Invalid("a table needs at least one column")
        if not self.alignments:
            self.alignments = ["default"] * len(self.headers)

    def _fit(self, cells: list[str]) -> list[str]:
        fitted = list(cells)[: len(self.headers)]
        fitted += [""] * (len(self.headers) - len(fitted))
        return fitted

    def add_row(self, cells: list[str]) -> TableBuilder:
        self.rows.append(self._fit(cells))
        return self

    def add_column(
        self, name: str, values: list[str] | None = None, align: str = "default"
    ) -> TableBuilder:
        self.headers.append(name)
        self.alignments.append(align)
        column = values or []
        for index, row in enumerate(self.rows):
            row.append(column[index] if index < len(column) else "")
        return self

    def set_cell(self, row: int, column: int, value: str) -> TableBuilder:
        if not 0 <= row < len(self.rows):
            raise Missing(f"row {row} of {len(self.rows)}")
        if not 0 <= column < len(self.headers):
            raise Missing(f"column {column} of {len(self.headers)}")
        self.rows[row][column] = value
        return self

    def delete_row(self, index: int) -> TableBuilder:
        if not 0 <= index < len(self.rows):
            raise Missing(f"row {index} of {len(self.rows)}")
        del self.rows[index]
        return self

    def sort_by(self, column: int, reverse: bool = False) -> TableBuilder:
        def cell(row: list[str]) -> str:
            return row[column] if column < len(row) else ""

        cells = [cell(row) for row in self.rows]
        numeric = bool(cells) and all(_is_number(value) for value in cells)
        if numeric:
            self.rows.sort(key=lambda row: float(cell(row)), reverse=reverse)
        else:
            self.rows.sort(key=cell, reverse=reverse)
        return self

    def to_table(self) -> Table:
        return Table(
            headers=list(self.headers),
            alignments=list(self.alignments),
            rows=[list(row) for row in self.rows],
        )

    def render(self) -> str:
        return render_table(self.to_table())

    def row_count(self) -> int:
        return len(self.rows)

    def column_count(self) -> int:
        return len(self.headers)


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True
