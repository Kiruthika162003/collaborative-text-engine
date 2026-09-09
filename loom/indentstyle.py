"""Indent style: infer whether a document indents with spaces or tabs, and how wide.

A document has an indentation style even when nobody wrote it
down, and a tool that reformats or a reviewer who cares about
consistency needs to know it. This reads the leading
whitespace of every line and infers the style: tabs if the
indents are tabs, spaces if they are spaces, and mixed, the
finding worth surfacing, if both appear, because a file that
indents some lines with tabs and others with spaces looks
aligned in one editor and ragged in the next and is the single
most common indentation bug. For space indentation it infers
the width as the smallest positive indent it sees, the
heuristic that reads a file stepped by two as two-wide and one
stepped by four as four-wide, and it is named as a heuristic
because a file whose shallowest indent happens to be a
one-space typo would be misread, which is the honest failure
mode of inferring a width from examples rather than being told
it. A flat document with no indentation has no style to infer
and says so, rather than defaulting to a style it has no
evidence for. It reads and reports, changing nothing, because
converting one style to another is the tabs module's job and
the writer's to ask for; this only tells them which style the
document is in, which is the question that has to be answered
before that conversion can be asked for at all.
"""

from __future__ import annotations

from loom.linewise import lines_of
from loom.weave import Weave


def _leading(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def uses_tabs(weave: Weave) -> bool:
    return any("\t" in _leading(line) for line in lines_of(weave))


def uses_spaces(weave: Weave) -> bool:
    return any(
        _leading(line) and "\t" not in _leading(line)
        for line in lines_of(weave)
    )


def is_mixed(weave: Weave) -> bool:
    return uses_tabs(weave) and uses_spaces(weave)


def indent_width(weave: Weave) -> int:
    widths = [
        len(_leading(line))
        for line in lines_of(weave)
        if _leading(line) and "\t" not in _leading(line)
    ]
    return min(widths) if widths else 0


def detect(weave: Weave) -> tuple[str, int]:
    tabs = uses_tabs(weave)
    spaces = uses_spaces(weave)
    if tabs and spaces:
        return ("mixed", indent_width(weave))
    if tabs:
        return ("tabs", 1)
    if spaces:
        return ("spaces", indent_width(weave))
    return ("none", 0)


def report(weave: Weave) -> str:
    kind, width = detect(weave)
    if kind == "none":
        return "no indentation; the document is flat"
    if kind == "tabs":
        return "indented with tabs"
    if kind == "mixed":
        return (
            "mixed indentation: both tabs and spaces; this looks "
            "aligned in one editor and ragged in the next"
        )
    return f"indented with spaces, width {width}"
