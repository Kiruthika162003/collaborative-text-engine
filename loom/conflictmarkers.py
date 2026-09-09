"""Conflict markers: parse the git-style conflict a document arrived carrying, and resolve it.

The loom's own merges converge without markers, but text
comes in from outside carrying the seven-angle-bracket scars
of a merge that did not, and a writer who pasted a conflicted
file wants to pick a side without hand-deleting the markers
and counting brackets. This reads those blocks, the ours side
above the equals line and the theirs side below it, bounded
by the opening and closing marker rows, and resolves one by
replacing the whole block with the chosen side as operations
every replica weaves. Only a complete block counts, an
opening, a divider, and a closing in that order, because a
lone marker row is more often a document about merge
conflicts than a real one, and resolving an imaginary
conflict would delete real text. Resolving takes a side by
name rather than guessing which is right, since which version
survives is the writer's decision and a tool that chose would
be overwriting one author's work on a coin toss. Resolving
all of them works from the document as it stands after each
choice rather than from a stale plan, so a block removed does
not shift the one still waiting into the wrong lines. An
empty side, a conflict where one branch deleted the lines, is
honoured as the deletion it is: choosing it leaves nothing
where the block was, rather than refusing because there was
nothing to insert.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.author import Author
from loom.errors import Invalid
from loom.linewise import lines_of, visible_index
from loom.weave import Op, Weave

OURS = re.compile(r"^<{7}( .*)?$")
MIDDLE = re.compile(r"^={7}$")
THEIRS = re.compile(r"^>{7}( .*)?$")


@dataclass(frozen=True)
class Conflict:
    start: int
    middle: int
    end: int
    ours: list[str]
    theirs: list[str]


def conflicts(weave: Weave) -> list[Conflict]:
    lines = lines_of(weave)
    result: list[Conflict] = []
    index = 0
    while index < len(lines):
        if not OURS.match(lines[index]):
            index += 1
            continue
        start = index
        cursor = index + 1
        ours: list[str] = []
        while cursor < len(lines) and not MIDDLE.match(lines[cursor]):
            if OURS.match(lines[cursor]) or THEIRS.match(lines[cursor]):
                break
            ours.append(lines[cursor])
            cursor += 1
        if cursor >= len(lines) or not MIDDLE.match(lines[cursor]):
            index += 1
            continue
        middle = cursor
        cursor += 1
        theirs: list[str] = []
        while cursor < len(lines) and not THEIRS.match(lines[cursor]):
            if OURS.match(lines[cursor]):
                break
            theirs.append(lines[cursor])
            cursor += 1
        if cursor >= len(lines) or not THEIRS.match(lines[cursor]):
            index += 1
            continue
        result.append(Conflict(start, middle, cursor, ours, theirs))
        index = cursor + 1
    return result


def resolve(author: Author, position: int, side: str) -> list[Op]:
    if side not in {"ours", "theirs"}:
        raise Invalid("a conflict is resolved to 'ours' or 'theirs'")
    found = conflicts(author.weave)
    conflict = found[position]
    chosen = conflict.ours if side == "ours" else conflict.theirs
    lines = lines_of(author.weave)
    start = visible_index(author.weave, conflict.start, 0)
    end = visible_index(author.weave, conflict.end, len(lines[conflict.end]))
    ops = author.erase_at(start, end - start)
    if chosen:
        ops.extend(author.type_at(start, "\n".join(chosen)))
    return ops


def resolve_all(author: Author, side: str) -> list[Op]:
    ops: list[Op] = []
    while conflicts(author.weave):
        ops.extend(resolve(author, 0, side))
    return ops


def has_conflicts(weave: Weave) -> bool:
    return bool(conflicts(weave))
