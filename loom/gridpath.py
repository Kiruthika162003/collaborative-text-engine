"""Grid path: shortest path across a grid of open cells and walls, by breadth-first search.

A grid where some cells are open and some are walls is the
simplest map, and the shortest number of steps from one cell to
another across it is a breadth-first search, which this
computes. Breadth-first is the right search because it explores
outward in rings of equal distance, so the first time it reaches
the goal it has reached it by a shortest path, and no path found
later could be shorter, which is what makes the answer the true
minimum without weighing alternatives. It moves in the four
orthogonal directions, up, down, left, and right, the
four-connectivity a grid usually means, treating a wall cell and
any cell off the edge as impassable, and it marks a cell seen
when it first reaches it so it never revisits, which both keeps
it fast and guarantees termination. The distance is the count of
steps, so an adjacent goal is one and the start is zero, and a
goal walled off from the start returns the not-found marker
rather than a wrong number, since no path exists and pretending
one does would be worse than saying so. The grid is read as rows
of cells where a wall is marked and everything else is open, and
the reachable query returns every cell the start can get to,
which maps the connected region and reveals which parts of a map
are sealed off. It finds the length of the shortest path, not
the path itself; a caller who needs the route keeps a
predecessor map, which this omits to stay the focused distance
search, the same choice the shortest-path graph module made.
"""

from __future__ import annotations

from collections import deque

Cell = tuple[int, int]
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))
WALL = "#"


def _passable(grid: list, row: int, col: int) -> bool:
    return (
        0 <= row < len(grid)
        and 0 <= col < len(grid[row])
        and grid[row][col] != WALL
    )


def shortest_path(grid: list, start: Cell, goal: Cell) -> int:
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (row, col), distance = queue.popleft()
        if (row, col) == goal:
            return distance
        for delta_row, delta_col in DIRECTIONS:
            step = (row + delta_row, col + delta_col)
            if _passable(grid, *step) and step not in seen:
                seen.add(step)
                queue.append((step, distance + 1))
    return -1


def reachable(grid: list, start: Cell) -> set:
    seen = {start}
    queue = deque([start])
    while queue:
        row, col = queue.popleft()
        for delta_row, delta_col in DIRECTIONS:
            step = (row + delta_row, col + delta_col)
            if _passable(grid, *step) and step not in seen:
                seen.add(step)
                queue.append(step)
    return seen
