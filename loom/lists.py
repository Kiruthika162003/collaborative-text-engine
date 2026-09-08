"""Lists: bulleted and numbered items read off the cloth, renumbered on the fly.

Writers make lists with dashes and digits, and this reads
them the way they typed them: a line starting with a dash
and a space is a bullet, a line starting with digits, a
dot, and a space is a numbered item, and leading spaces
set the nesting depth two spaces to a level. The numbers a
writer types are ignored for rendering and recomputed from
position, because the whole misery of hand-numbered lists
is that inserting item two renumbers everything below it by
hand, and a list tool that preserves the typed numbers has
automated nothing. Renumbering restarts at each depth and
each break in the run, so a nested list counts one two
three inside its parent's item rather than continuing the
outer count, which is what every reader expects and no
plain-text format enforces. A line that is neither bullet
nor number breaks the list, because a paragraph between two
items is two lists, and pretending otherwise glues
unrelated things into one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.weave import Weave

BULLET = re.compile(r"^( *)- (.*)$")
NUMBERED = re.compile(r"^( *)\d+\. (.*)$")


@dataclass(frozen=True)
class Item:
    depth: int
    kind: str
    text: str
    number: int


def _lines(weave: Weave) -> list[str]:
    return weave.text().split("\n")


def items(weave: Weave) -> list[Item]:
    found: list[Item] = []
    counters: dict[int, int] = {}
    for raw in _lines(weave):
        bullet = BULLET.match(raw)
        numbered = NUMBERED.match(raw)
        match = bullet or numbered
        if match is None:
            counters.clear()
            continue
        depth = len(match.group(1)) // 2
        kind = "bullet" if bullet else "numbered"
        for deeper in list(counters):
            if deeper > depth:
                del counters[deeper]
        counters[depth] = counters.get(depth, 0) + 1
        found.append(
            Item(
                depth=depth,
                kind=kind,
                text=match.group(2),
                number=counters[depth],
            )
        )
    return found


def render(weave: Weave) -> str:
    found = items(weave)
    if not found:
        return "no list items in the cloth"
    lines = []
    for item in found:
        indent = "  " * item.depth
        marker = (
            "-"
            if item.kind == "bullet"
            else f"{item.number}."
        )
        lines.append(f"{indent}{marker} {item.text}")
    return "\n".join(lines)


def deepest(weave: Weave) -> int:
    found = items(weave)
    return max((item.depth for item in found), default=-1) + 1
