"""A star: find a shortest grid path guided toward the goal, not blindly.

Breadth-first search finds a shortest path on a grid by expanding
outward in rings of equal distance, which is correct but blind: it
spends as much effort walking away from the goal as toward it,
because it has no notion of which direction the goal lies. A star
keeps the same guarantee of a shortest path but adds that notion. It
orders the cells it is willing to expand not by distance from the
start alone but by that distance plus an estimate of the distance
still to go, and it always expands the cell whose sum is smallest,
so the search leans toward the goal and reaches it after touching a
fraction of the cells the blind ring-expansion would. The estimate
here is the Manhattan distance, the steps a piece would take with no
walls in the way, which on a four-connected grid can never
overestimate the true remaining distance, and that never-overestimate
property is exactly what keeps the answer optimal: because the
estimate is never too high, the first time the goal is pulled off the
queue it has been reached by a genuine shortest path, not a hasty
one. I had guessed A star would only beat breadth-first with a
finely tuned heuristic and would otherwise just pay for a priority
queue it did not earn; even this plain Manhattan estimate, the
obvious one, steers the search enough that it settles far fewer
cells than breadth-first on an open grid, and the guidance costs
nothing in optimality because the estimate stays honest. Where walls
force long detours the estimate is a poor guide and A star settles
more cells, drifting back toward breadth-first's effort, which is the
honest boundary: the heuristic helps in proportion to how well
straight-line distance predicts the real path, and it never hurts
correctness. This returns the path itself, the sequence of cells from
start to goal, reconstructed by remembering which cell each was first
reached from, where the breadth-first module returned only the
distance; the length of that path is one less than its cell count and
agrees with the distance the blind search reports.
"""

from __future__ import annotations

import heapq

Cell = tuple[int, int]
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))
WALL = "#"


def _passable(grid: list, row: int, col: int) -> bool:
    return 0 <= row < len(grid) and 0 <= col < len(grid[row]) and grid[row][col] != WALL


def _manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def shortest_path(grid: list, start: Cell, goal: Cell) -> list | None:
    if not _passable(grid, *start) or not _passable(grid, *goal):
        return None
    open_heap = [(_manhattan(start, goal), 0, start)]
    came_from: dict = {start: None}
    best = {start: 0}
    while open_heap:
        _, cost, current = heapq.heappop(open_heap)
        if current == goal:
            return _reconstruct(came_from, goal)
        if cost > best[current]:
            continue
        row, col = current
        for delta_row, delta_col in DIRECTIONS:
            step = (row + delta_row, col + delta_col)
            if not _passable(grid, *step):
                continue
            tentative = cost + 1
            if step not in best or tentative < best[step]:
                best[step] = tentative
                came_from[step] = current
                heapq.heappush(open_heap, (tentative + _manhattan(step, goal), tentative, step))
    return None


def _reconstruct(came_from: dict, goal: Cell) -> list:
    path = [goal]
    node = came_from[goal]
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def path_length(grid: list, start: Cell, goal: Cell) -> int:
    path = shortest_path(grid, start, goal)
    return len(path) - 1 if path is not None else -1
