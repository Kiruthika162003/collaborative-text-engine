from __future__ import annotations

from loom.gridpath import reachable, shortest_path


class TestShortestPath:
    def test_open_grid(self):
        grid = ["...", "...", "..."]
        assert shortest_path(grid, (0, 0), (2, 2)) == 4

    def test_start_equals_goal(self):
        assert shortest_path(["..", ".."], (0, 0), (0, 0)) == 0

    def test_a_wall_forces_a_detour(self):
        grid = [
            ".#.",
            ".#.",
            "...",
        ]
        assert shortest_path(grid, (0, 0), (0, 2)) == 6

    def test_a_walled_off_goal_is_unreachable(self):
        grid = [
            ".#.",
            "###",
            ".#.",
        ]
        assert shortest_path(grid, (0, 0), (2, 2)) == -1


class TestReachable:
    def test_the_connected_region(self):
        grid = [
            "..#",
            ".##",
            "..#",
        ]
        cells = reachable(grid, (0, 0))
        assert (2, 1) in cells
        assert (0, 2) not in cells

    def test_a_sealed_cell_reaches_only_itself(self):
        grid = [
            "#.#",
            "#.#",
        ]
        assert reachable(grid, (0, 1)) == {(0, 1), (1, 1)}
