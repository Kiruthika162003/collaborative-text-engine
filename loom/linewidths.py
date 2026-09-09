"""Line widths: which lines run past a column, measured the way a terminal sees them.

A document meant to fit a column has lines that quietly grow
past it, and this finds them, measuring each line's width the
way the columns module measures a caret, by display cells
rather than glyph count, so a line of Chinese that fills forty
cells is forty wide even though it holds twenty characters.
That is the honest measure for the question, because the limit
a writer sets is a visual one, the edge of the page or the
terminal, and counting glyphs would pass a line that overflows
and flag one that does not. It reports the lines over a given
limit with their widths, names the longest line and its width,
and lists the widths in order for a caller that wants the
whole profile, all as readings that change nothing, since
whether a long line should be wrapped is the reflow module's
job to do and the writer's to ask for. Tabs are counted at
their expanded width so a line indented with tabs measures as
it displays, and the limit is the caller's because the right
column is the document's convention, not a number this module
should presume; it measures against whatever edge it is
given.
"""

from __future__ import annotations

from loom.columns import display_width
from loom.linewise import lines_of
from loom.weave import Weave


def widths(weave: Weave) -> list[int]:
    return [display_width(line) for line in lines_of(weave)]


def over_limit(weave: Weave, limit: int) -> list[tuple[int, int]]:
    return [
        (number, width)
        for number, width in enumerate(widths(weave))
        if width > limit
    ]


def longest_line(weave: Weave) -> tuple[int, int]:
    profile = widths(weave)
    if not profile:
        return (-1, 0)
    widest = max(profile)
    return (profile.index(widest), widest)


def report(weave: Weave, limit: int) -> str:
    over = over_limit(weave, limit)
    if not over:
        return f"every line fits within {limit} column(s)"
    lines = [f"{len(over)} line(s) over {limit} column(s):"]
    for number, width in over:
        lines.append(f"  line {number}: {width} column(s)")
    return "\n".join(lines)
