"""Headings: the document's outline read off its own hash-marked lines.

Long documents are navigated by their headings, and this
module reads them the way a Markdown writer already writes
them, a line beginning with one to six hash marks and a
space, its level the count of hashes. The outline is
built by nesting each heading under the nearest preceding
heading of a shallower level, which is how a table of
contents actually reads, and a heading that jumps more than
one level deeper than its parent, a level-one followed by
a level-three, is recorded with a gap note rather than
silently reparented, because a skipped level is usually a
typo and always a thing the writer wants to see. Each
heading pins to the strand of its first hash, so a
navigation link to a section survives the section moving,
the same pin discipline every anchor in this codebase
uses. The depth of the deepest heading and the count at
each level are reported because those are the numbers that
tell a writer their document has grown a structure it
never designed.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    pin: OpId
    gap: bool


def _visible_lines(weave: Weave):
    line_glyphs = []
    line_first = None
    for strand in weave.strands:
        if strand.sheared:
            continue
        if strand.glyph == "\n":
            yield line_first, "".join(line_glyphs)
            line_glyphs = []
            line_first = None
            continue
        if line_first is None:
            line_first = strand.id
        line_glyphs.append(strand.glyph)
    yield line_first, "".join(line_glyphs)


def _parse_heading(text: str):
    stripped = text.lstrip("#")
    level = len(text) - len(stripped)
    if 1 <= level <= 6 and stripped.startswith(" "):
        return level, stripped[1:].strip()
    return None


def headings(weave: Weave) -> list[Heading]:
    found: list[Heading] = []
    last_level = 0
    for pin, text in _visible_lines(weave):
        parsed = _parse_heading(text)
        if parsed is None or pin is None:
            continue
        level, title = parsed
        gap = (
            level > last_level + 1 and last_level > 0
        )
        found.append(
            Heading(
                level=level,
                title=title,
                pin=pin,
                gap=gap,
            )
        )
        last_level = level
    return found


def outline(weave: Weave) -> str:
    found = headings(weave)
    if not found:
        return "no headings; the document is flat"
    lines = [f"{len(found)} heading(s):"]
    for heading in found:
        indent = "  " * (heading.level - 1)
        note = (
            " [level gap; a skipped level is usually "
            "a typo]"
            if heading.gap
            else ""
        )
        lines.append(
            f"{indent}{heading.title}{note}"
        )
    return "\n".join(lines)


def depth(weave: Weave) -> int:
    found = headings(weave)
    return max((h.level for h in found), default=0)


def level_counts(weave: Weave) -> dict[int, int]:
    counts: dict[int, int] = {}
    for heading in headings(weave):
        counts[heading.level] = (
            counts.get(heading.level, 0) + 1
        )
    return counts
