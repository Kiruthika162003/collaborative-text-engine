"""Line diff: the added and removed lines between two texts, at line granularity.

The patch module diffs at the character level to mint minimal
operations, and the word-diff module works within a line; this
works at the line level, the granularity a reviewer reads a
change at, marking each line kept, removed, or added between a
before and an after. It leans on the standard library's
sequence matcher for the alignment and turns the opcodes into
the plus-and-minus stream a reader knows from every diff tool:
a space for a line that stayed, a minus for one that left, a
plus for one that arrived, and a changed line shown as its old
form removed and its new form added, because at line
granularity a line that changed at all is a different line.
That last point is the honest limit and it is stated: a line
where a single word changed shows here as a whole line gone
and a whole line come, not as the one word; a reader who wants
to see which word moved reaches for the word-diff module,
which works inside the line this one treats as atomic. The
counts of added and removed lines fall out of the same stream,
the two numbers a reviewer asks first, and a changed predicate
answers the yes-or-no without rendering the whole diff. It
renders, it does not apply: turning a target text into the
document is the patch module's job, and this only shows the
shape of the difference for a human to read.
"""

from __future__ import annotations

import difflib


def line_ops(before: str, after: str) -> list[tuple[str, str]]:
    old = before.split("\n")
    new = after.split("\n")
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    ops: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {"delete", "replace"}:
            ops.extend(("-", line) for line in old[i1:i2])
        if tag in {"insert", "replace"}:
            ops.extend(("+", line) for line in new[j1:j2])
        if tag == "equal":
            ops.extend((" ", line) for line in old[i1:i2])
    return ops


def render(before: str, after: str) -> str:
    return "\n".join(f"{mark}{line}" for mark, line in line_ops(before, after))


def added(before: str, after: str) -> int:
    return sum(1 for mark, _line in line_ops(before, after) if mark == "+")


def removed(before: str, after: str) -> int:
    return sum(1 for mark, _line in line_ops(before, after) if mark == "-")


def changed(before: str, after: str) -> bool:
    return before != after
