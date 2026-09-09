"""Side by side: lay several text blocks in columns, aligned and padded to fit.

Comparing two versions, or laying notes beside a draft, wants
the blocks shown in parallel columns rather than stacked, and
this arranges them: each block's lines padded to its own widest
line so its right edge is straight, the blocks joined left to
right with a gap between, and blocks of unequal height padded
with blank space below the shorter ones so every column runs
the full height. The padding is measured by display width, so a
block holding a wide glyph keeps its neighbour's column from
drifting, the same alignment the box and table renderers trust.
Trailing whitespace on each assembled row is trimmed, because
the padding exists to align the columns to its left and a run
of spaces off the right edge is invisible clutter a diff tool
flags; the internal padding that does the aligning stays, only
the tail past the last column goes. The gap between columns is
the caller's, two spaces by default, wide enough to read as a
gutter and narrow enough not to waste a terminal's width. It is
pure rendering returning a string, joining blocks a caller
produced however they produced them, so the same layout serves
a diff, a comparison, or a two-up notes view without knowing
what the blocks mean, which is the right level for a layout
primitive to work at.
"""

from __future__ import annotations

from loom.columns import display_width, pad_to


def side_by_side(blocks: list[str], gap: int = 2) -> str:
    if not blocks:
        return ""
    grids = [block.split("\n") for block in blocks]
    height = max((len(grid) for grid in grids), default=0)
    widths = [
        max((display_width(line) for line in grid), default=0)
        for grid in grids
    ]
    separator = " " * gap
    rows = []
    for row in range(height):
        cells = []
        for index, grid in enumerate(grids):
            line = grid[row] if row < len(grid) else ""
            cells.append(pad_to(line, widths[index]))
        rows.append(separator.join(cells).rstrip())
    return "\n".join(rows)
