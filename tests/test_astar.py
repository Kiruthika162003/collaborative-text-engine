from __future__ import annotations

from itertools import pairwise

from loom.astar import path_length, shortest_path
from loom.gridpath import shortest_path as bfs_distance


class TestPath:
    def test_a_straight_path_on_an_open_grid(self):
        grid = ["...", "...", "..."]
        path = shortest_path(grid, (0, 0), (2, 2))
        assert path[0] == (0, 0)
        assert path[-1] == (2, 2)
        assert len(path) - 1 == 4

    def test_start_equals_goal(self):
        assert shortest_path(["..", ".."], (1, 1), (1, 1)) == [(1, 1)]

    def test_a_wall_forces_a_detour(self):
        grid = [
            ".#.",
            ".#.",
            "...",
        ]
        assert path_length(grid, (0, 0), (0, 2)) == 6

    def test_a_walled_off_goal_has_no_path(self):
        grid = [
            ".#.",
            "###",
            ".#.",
        ]
        assert shortest_path(grid, (0, 0), (2, 2)) is None
        assert path_length(grid, (0, 0), (2, 2)) == -1

    def test_a_wall_start_is_rejected(self):
        assert shortest_path(["#.", ".."], (0, 0), (1, 1)) is None


class TestPathIsValid:
    def test_every_step_is_adjacent_and_open(self):
        grid = [
            "......",
            ".####.",
            ".#....",
            ".#.##.",
            "...#..",
        ]
        path = shortest_path(grid, (0, 0), (4, 5))
        assert path is not None
        for (r1, c1), (r2, c2) in pairwise(path):
            assert abs(r1 - r2) + abs(c1 - c2) == 1
            assert grid[r2][c2] != "#"


class TestAgreesWithBreadthFirst:
    def test_lengths_match_the_bfs_distance(self):
        grids = [
            ["...", "...", "..."],
            [".#.", ".#.", "..."],
            ["......", ".####.", ".#....", ".#.##.", "...#.."],
            ["....", "....", "....", "...."],
        ]
        for grid in grids:
            assert path_length(grid, (0, 0), (len(grid) - 1, len(grid[0]) - 1)) == bfs_distance(
                grid, (0, 0), (len(grid) - 1, len(grid[0]) - 1)
            )
