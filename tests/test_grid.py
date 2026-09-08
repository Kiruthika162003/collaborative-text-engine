from __future__ import annotations

import pytest

from loom.errors import Missing
from loom.grid import Grid
from loom.ids import OpId


def rid(site: str, n: int) -> OpId:
    return OpId(site=site, counter=n)


def small_grid() -> tuple[Grid, list, list]:
    grid = Grid()
    rows = [rid("alice", 1), rid("alice", 2)]
    cols = [rid("alice", 10), rid("alice", 11)]
    for r in rows:
        grid.add_row(r)
    for c in cols:
        grid.add_col(c)
    return grid, rows, cols


class TestStableIdentity:
    def test_cells_addressed_by_id_not_index(self):
        grid, rows, cols = small_grid()
        grid.set_cell(rows[1], cols[0], "here", rank=1)
        grid.add_row(rid("bob", 5))
        grid.rows.sort(
            key=lambda i: (i.counter, i.site)
        )
        assert grid.get_cell(rows[1], cols[0]) == "here"

    def test_concurrent_rows_land_in_agreed_order(self):
        one = Grid()
        two = Grid()
        r1 = rid("alice", 3)
        r2 = rid("bob", 3)
        one.add_row(r1)
        one.add_row(r2)
        two.add_row(r2)
        two.add_row(r1)
        assert one.rows == two.rows

    def test_a_cell_in_a_missing_row_is_refused(self):
        grid, _rows, cols = small_grid()
        with pytest.raises(Missing):
            grid.set_cell(
                rid("zed", 9), cols[0], "x", rank=1
            )


class TestCellWrites:
    def test_the_later_write_wins(self):
        grid, rows, cols = small_grid()
        grid.set_cell(rows[0], cols[0], "old", rank=2)
        grid.set_cell(rows[0], cols[0], "new", rank=5)
        assert grid.get_cell(rows[0], cols[0]) == "new"

    def test_an_early_write_yields(self):
        grid, rows, cols = small_grid()
        grid.set_cell(rows[0], cols[0], "keep", rank=9)
        receipt = grid.set_cell(
            rows[0], cols[0], "late", rank=2
        )
        assert "yielded" in receipt
        assert grid.get_cell(rows[0], cols[0]) == "keep"


class TestShape:
    def test_a_deleted_row_leaves_the_shape(self):
        grid, rows, _cols = small_grid()
        grid.delete_row(rows[0])
        assert grid.shape() == (1, 2)

    def test_render_shows_blanks_not_holes(self):
        grid, rows, cols = small_grid()
        grid.set_cell(rows[0], cols[0], "x", rank=1)
        page = grid.render()
        assert "x | -" in page

    def test_an_empty_grid_says_so(self):
        assert "an empty grid" in Grid().render()
