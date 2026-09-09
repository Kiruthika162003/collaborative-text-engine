"""Section numbers: write the outline's numbers into the heading text, and take them back.

The table of contents renders a heading tree with dotted
numbers, one, one point one, two, but those numbers live in
the view; the heading in the document still reads Background,
not 1.1 Background. This writes them in, editing each heading
line so its number stands in the text where a reader and a
printer both see it, and it takes them back out again, the
two directions a writer toggles while a document grows. The
numbers come from the same walk the contents uses, so the
text and the contents cannot disagree, and writing them is
minting operations, shearing the stale prefix if one is there
and weaving the right one, so every replica converges on the
numbered text rather than one screen showing numbers the
others lack. Running it twice is safe because it strips any
existing number before writing the new one, so numbering an
already-numbered document corrects the numbers instead of
stacking them. What counts as an existing number depends on
the heading's depth, which is where the genuine ambiguity is
handled honestly: a subsection's number is always dotted, one
point one, so a deeper heading titled with a bare year keeps
it, the dot being the tell that separates a section number
from a quantity. A top-level heading is the one place the
ambiguity cannot be dodged, because its number is a bare
integer and so is a year, and there the numbering treats a
leading integer as its own, the same unavoidable coin the
slash date has to call. A leading decimal like three point
one four at any depth reads as a section number too, and that
is named rather than hidden.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.linewise import lines_of, visible_index
from loom.toc import entries
from loom.weave import Op, Weave

HEADING = re.compile(r"^(#{1,6})( +)(.*)$")
TOP_PREFIX = re.compile(r"^\d+(?:\.\d+)*\s+")
DEEP_PREFIX = re.compile(r"^\d+(?:\.\d+)+\s+")


def _bare(title: str, level: int) -> str:
    pattern = TOP_PREFIX if level == 1 else DEEP_PREFIX
    match = pattern.match(title)
    stripped = title[match.end() :] if match else title
    return stripped.strip()


def _infos(weave: Weave) -> list[tuple[str, int]]:
    return [(entry.number, entry.level) for entry in entries(weave)]


def _plan(
    author: Author, infos: list[tuple[str, int]], writing: bool
) -> list[tuple[int, int, int, str]]:
    plan: list[tuple[int, int, int, str]] = []
    heading_index = 0
    for line_no, raw in enumerate(lines_of(author.weave)):
        match = HEADING.match(raw)
        if match is None:
            continue
        number, level = infos[heading_index]
        heading_index += 1
        column = len(match.group(1)) + len(match.group(2))
        current = match.group(3)
        bare = _bare(current, level)
        desired = f"{number} {bare}".strip() if writing else bare
        if current != desired:
            plan.append((line_no, column, len(current), desired))
    return plan


def _apply(author: Author, plan: list[tuple[int, int, int, str]]) -> list[Op]:
    ops: list[Op] = []
    for line_no, column, length, desired in plan:
        index = visible_index(author.weave, line_no, column)
        ops.extend(author.erase_at(index, length))
        if desired:
            ops.extend(author.type_at(index, desired))
    return ops


def number_headings(author: Author) -> list[Op]:
    return _apply(author, _plan(author, _infos(author.weave), writing=True))


def strip_numbers(author: Author) -> list[Op]:
    return _apply(author, _plan(author, _infos(author.weave), writing=False))


def preview(weave: Weave) -> str:
    infos = _infos(weave)
    found = entries(weave)
    if not found:
        return "no headings to number"
    return "\n".join(
        f"{infos[index][0]} {_bare(entry.title, entry.level)}"
        for index, entry in enumerate(found)
    )
