"""CSV table: a queryable view over parsed CSV, rows as dicts and columns by name.

The commas module parses CSV into rows of strings; this wraps
that into a table a caller queries by name rather than by
index, which is how a caller thinks about tabular data once it
has a header. It reads the first row as the header and the rest
as data, exposes each row as a dict keyed by the header so a
caller writes row['name'] rather than counting to the right
column, and offers the operations that follow from that: a
column by name, a projection down to chosen columns, a filter
over the row dicts, and a sort by a named column. Selecting
columns and filtering rows return new tables rather than
mutating this one, so a chain of queries leaves the original
intact and a caller can branch a query without copying by
hand. A row shorter than the header reads its missing columns
as empty strings rather than raising, keeping with the commas
module's tolerance of ragged data, and asking for a column the
header does not have is the one hard error, refused with the
header named, because a typo in a column name is a bug a caller
wants pointed at rather than answered with an empty column that
looks like real but absent data. It renders back to CSV through
the commas renderer, so a table read, queried, and rendered
comes out as valid CSV, and the read-query-write round trip
that a data pipeline needs holds without leaving this module.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from loom.commas import parse
from loom.commas import render as render_csv
from loom.errors import Missing


@dataclass
class CsvTable:
    headers: list[str]
    rows: list[list[str]]

    @classmethod
    def read(cls, text: str) -> CsvTable:
        parsed = parse(text)
        if not parsed:
            return cls(headers=[], rows=[])
        return cls(headers=parsed[0], rows=parsed[1:])

    def _index(self, name: str) -> int:
        if name not in self.headers:
            raise Missing(
                f"no column {name!r}; the header is {self.headers}"
            )
        return self.headers.index(name)

    def dicts(self) -> list[dict[str, str]]:
        return [
            {
                header: row[position] if position < len(row) else ""
                for position, header in enumerate(self.headers)
            }
            for row in self.rows
        ]

    def column(self, name: str) -> list[str]:
        index = self._index(name)
        return [
            row[index] if index < len(row) else "" for row in self.rows
        ]

    def select(self, *names: str) -> CsvTable:
        indices = [self._index(name) for name in names]
        rows = [
            [row[index] if index < len(row) else "" for index in indices]
            for row in self.rows
        ]
        return CsvTable(headers=list(names), rows=rows)

    def where(
        self, predicate: Callable[[dict[str, str]], bool]
    ) -> CsvTable:
        kept = [
            row
            for row, record in zip(self.rows, self.dicts(), strict=True)
            if predicate(record)
        ]
        return CsvTable(headers=list(self.headers), rows=kept)

    def sort_by(self, name: str, reverse: bool = False) -> CsvTable:
        index = self._index(name)

        def key(row: list[str]) -> str:
            return row[index] if index < len(row) else ""

        return CsvTable(
            headers=list(self.headers),
            rows=sorted(self.rows, key=key, reverse=reverse),
        )

    def render(self) -> str:
        return render_csv([self.headers, *self.rows])

    def row_count(self) -> int:
        return len(self.rows)
