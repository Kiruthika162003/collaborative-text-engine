"""Bar chart: render labeled values as a horizontal bar chart in text.

Counts read better as bars than as a column of numbers, and
this renders a list of label-value pairs as a horizontal chart,
each bar scaled so the largest value fills the chart's width
and the rest show in proportion. Scaling to the largest value
is the choice that makes one chart readable and it is stated,
because it means the bars show proportions within this chart,
not absolute magnitudes across charts: two charts drawn
separately cannot be compared by bar length unless the caller
fixes a common scale, which this leaves to them rather than
guessing a maximum. Labels are right-aligned into a column as
wide as the longest, so the bars start from a straight edge and
the eye reads down them, and the value is printed after each
bar so the exact number is there for anyone who wants it past
the shape. Zero shows as no bar rather than a single forced
character, because a zero that drew a bar would read as a
small value rather than none, and the width is the caller's
since the right size depends on the terminal it lands in. It
renders non-negative values, and that is named: a chart mixing
positive and negative bars needs a zero axis and a direction
this simple renderer does not draw, so a caller with signed
data wants a chart that does, not this one pretending.
"""

from __future__ import annotations

DEFAULT_WIDTH = 40


def chart(pairs: list[tuple[str, int]], width: int = DEFAULT_WIDTH) -> str:
    if not pairs:
        return "no data to chart"
    biggest = max((value for _label, value in pairs), default=0) or 1
    label_width = max(len(str(label)) for label, _value in pairs)
    lines = []
    for label, value in pairs:
        length = round(max(value, 0) / biggest * width)
        bar = "#" * length
        lines.append(f"{str(label).rjust(label_width)} | {bar} {value}")
    return "\n".join(lines)


def bar_length(value: int, biggest: int, width: int = DEFAULT_WIDTH) -> int:
    if biggest <= 0:
        return 0
    return round(max(value, 0) / biggest * width)
