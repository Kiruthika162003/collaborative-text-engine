"""Grid: a table whose cells converge and whose rows carry stable identities.

A collaborative table breaks in a specific place: two people
insert a row at once and a positional model shuffles
everyone's data into the wrong rows. The grid avoids it by
giving every row and column a stable id, minted like a
strand with a site and counter, and ordering them by that
id the same way the weave orders glyphs, so two concurrent
row inserts land in an order every replica agrees on rather
than colliding on an index. A cell is addressed by the pair
of ids, not by coordinates, and holds a last-writer-wins
value keyed by witness rank, so editing the cell at row
three column two means the same cell on every machine even
after rows moved above it. Deleting a row tombstones its id
so cells still addressed by a late arrival resolve rather
than crash, the same tombstone discipline the text uses,
and the rendered grid reads rows and columns in id order
with empty cells shown as blank rather than missing,
because a table with holes punched by absent cells is a
table that lies about its own shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Missing
from loom.ids import OpId


@dataclass
class Grid:
    rows: list = field(default_factory=list)
    cols: list = field(default_factory=list)
    dead_rows: set = field(default_factory=set)
    dead_cols: set = field(default_factory=set)
    cells: dict = field(default_factory=dict)

    def _insert_ordered(self, seq: list, op_id: OpId):
        if op_id in seq:
            return
        seq.append(op_id)
        seq.sort(key=lambda i: (i.counter, i.site))

    def add_row(self, row_id: OpId) -> str:
        self._insert_ordered(self.rows, row_id)
        return f"row {row_id.wire()} added"

    def add_col(self, col_id: OpId) -> str:
        self._insert_ordered(self.cols, col_id)
        return f"column {col_id.wire()} added"

    def set_cell(
        self,
        row_id: OpId,
        col_id: OpId,
        value: str,
        rank: int,
    ) -> str:
        if row_id not in self.rows:
            raise Missing(
                f"row {row_id.wire()} is not in the "
                "grid. Buffer it"
            )
        if col_id not in self.cols:
            raise Missing(
                f"column {col_id.wire()} is not in "
                "the grid. Buffer it"
            )
        key = (row_id, col_id)
        held = self.cells.get(key)
        if held is None or rank > held[0] or (
            rank == held[0]
            and row_id.site > held[2]
        ):
            self.cells[key] = (rank, value, row_id.site)
            return "cell set"
        return "cell write yielded to a later one"

    def get_cell(
        self, row_id: OpId, col_id: OpId
    ) -> str:
        held = self.cells.get((row_id, col_id))
        return held[1] if held else ""

    def delete_row(self, row_id: OpId) -> str:
        if row_id not in self.rows:
            raise Missing(
                f"row {row_id.wire()} is not here"
            )
        self.dead_rows.add(row_id)
        return f"row {row_id.wire()} tombstoned"

    def live_rows(self) -> list:
        return [
            r for r in self.rows if r not in self.dead_rows
        ]

    def live_cols(self) -> list:
        return [
            c for c in self.cols if c not in self.dead_cols
        ]

    def render(self) -> str:
        rows = self.live_rows()
        cols = self.live_cols()
        if not rows or not cols:
            return "an empty grid; no rows or no columns"
        lines = []
        for row_id in rows:
            cells = [
                self.get_cell(row_id, col_id) or "-"
                for col_id in cols
            ]
            lines.append(" | ".join(cells))
        return "\n".join(lines)

    def shape(self) -> tuple[int, int]:
        return len(self.live_rows()), len(
            self.live_cols()
        )
