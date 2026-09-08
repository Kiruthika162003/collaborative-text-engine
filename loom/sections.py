"""Sections: moving a whole heading-delimited block the only way a CRDT can.

Reordering a document means moving a section, and a
sequence CRDT has no move primitive, because a move is a
delete and a reinsert and pretending otherwise invents an
operation the convergence proof never covered. So this
does it honestly: it reads the section from its heading to
the line before the next heading of the same or shallower
level, shears every strand of that block, and reinserts the
same text at the destination, minting ordinary operations
that any replica weaves to the same result. The cost is
visible and owned: the moved text gets new strand ids, so
a comment pinned inside the moved section is orphaned by
the move, which is correct and honest, because the strands
it pinned to are genuinely gone, and a move that pretended
to preserve them would be lying about identity to save
face. The destination is named by the heading to place the
section before, or the end, and moving a section to inside
itself is refused, since a block cannot contain its own
relocation without eating its own tail.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.headings import headings


@dataclass(frozen=True)
class SectionMove:
    title: str
    text: str
    start_line: int
    end_line: int


def _heading_level(line: str) -> int:
    stripped = line.lstrip("#")
    level = len(line) - len(stripped)
    if 1 <= level <= 6 and stripped.startswith(" "):
        return level
    return 0


def _section_bounds(author: Author, title: str):
    found = headings(author.weave)
    lines = author.text().split("\n")
    match = next(
        (h for h in found if h.title == title), None
    )
    if match is None:
        raise Missing(
            f"no section titled {title!r}; the "
            "outline holds "
            + ", ".join(h.title for h in found)
        )
    heading_line = next(
        line_no
        for line_no, line in enumerate(lines)
        if _heading_level(line) == match.level
        and line.lstrip("#")[1:].strip() == title
    )
    end_line = len(lines)
    for line_no in range(heading_line + 1, len(lines)):
        level = _heading_level(lines[line_no])
        if level and level <= match.level:
            end_line = line_no
            break
    return heading_line, end_line


def move_section(
    author: Author, title: str, before: str | None
) -> str:
    heading_line, end_line = _section_bounds(
        author, title
    )
    lines = author.text().split("\n")
    if before is not None and before == title:
        raise Invalid(
            "a section cannot move to inside itself "
            "without eating its own tail"
        )
    block = lines[heading_line:end_line]
    block_text = "\n".join(block)

    start_index = (
        sum(len(line) + 1 for line in lines[:heading_line])
    )
    char_count = len("\n".join(block))
    trailing = 1 if end_line < len(lines) else 0
    author.erase_at(
        start_index, char_count + trailing
    )

    if before is None:
        dest = author.weave.visible_count()
        author.type_at(dest, "\n" + block_text)
    else:
        target_line, _ = _section_bounds(author, before)
        remaining = author.text().split("\n")
        dest = sum(
            len(line) + 1
            for line in remaining[:target_line]
        )
        author.type_at(dest, block_text + "\n")
    return (
        f"moved {title!r} ({len(block)} line(s)); new "
        "strand ids, orphaning any pins inside"
    )
