"""Diff view: show two texts side by side, old on the left and new on the right.

The line-diff module gives the plus-and-minus stream; this
arranges it into the two-column view a reviewer reads, the old
text down the left and the new down the right, aligned so a
changed line's old and new forms sit on the same row. The
arrangement is the work: context lines that both texts share
appear on both sides of the same row, but a run of deletions
and the run of additions that replaced them are buffered and
then paired row by row, so a block where three lines became two
shows the three olds beside the two news with a blank filling
the short side, rather than the olds and news stacked in a
column that hides which replaced which. That pairing is a
heuristic about intent, that adjacent deletions and additions
correspond, and it is the same heuristic every side-by-side
diff makes; it reads right for a straightforward edit and can
mis-pair a reordering, which is the honest limit of showing a
line diff in two columns rather than a full move-aware one. The
columns are laid out by the side-by-side module, so they align
by display width and the divide stays straight whatever the
lines hold, and the result is a string a terminal prints, a
review aid and not an edit, since applying a chosen version is
the patch module's job and this only shows the two to choose
between.
"""

from __future__ import annotations

from loom.linediff import line_ops
from loom.sidebyside import side_by_side


def side_diff(before: str, after: str) -> str:
    left: list[str] = []
    right: list[str] = []
    removed: list[str] = []
    added: list[str] = []

    def flush() -> None:
        for index in range(max(len(removed), len(added))):
            left.append(removed[index] if index < len(removed) else "")
            right.append(added[index] if index < len(added) else "")
        removed.clear()
        added.clear()

    for mark, line in line_ops(before, after):
        if mark == " ":
            flush()
            left.append(line)
            right.append(line)
        elif mark == "-":
            removed.append(line)
        else:
            added.append(line)
    flush()
    return side_by_side(["\n".join(left), "\n".join(right)])
