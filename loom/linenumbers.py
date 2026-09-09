"""Line numbers: render the text with a right-aligned number gutter for reference.

Pointing at a line by its number is how people talk about a
document over a call, and this renders the text with that
number in a gutter, right-aligned so the numbers form a clean
column no matter how many digits they grow to. It is a pure
rendering and changes nothing: the numbers are not woven into
the text, because a number a reader added to talk about a line
is not part of the line, and baking it in would corrupt the
very text it was meant to reference. Blank lines are numbered
like any other, since a blank line is still a line a reader
counts and skipping it would make every number below it wrong
by one, the exact confusion the gutter exists to prevent. The
starting number is the caller's, defaulting to one, because a
fragment shown from the middle of a larger document should
carry the numbers it has there, not restart at one and lie
about where it sits. The gutter width is computed from the
largest number it will hold, so a hundred-line document
aligns its single and triple digit numbers in one column
rather than stair-stepping, which is the difference between a
gutter a reader can scan and a ragged margin they cannot.
"""

from __future__ import annotations

from loom.weave import Weave


def numbered(text: str, start: int = 1) -> str:
    lines = text.split("\n")
    last = start + len(lines) - 1
    width = len(str(last))
    return "\n".join(
        f"{str(start + offset).rjust(width)}  {line}"
        for offset, line in enumerate(lines)
    )


def numbered_weave(weave: Weave, start: int = 1) -> str:
    return numbered(weave.text(), start)


def gutter_width(text: str, start: int = 1) -> int:
    return len(str(start + text.count("\n")))
