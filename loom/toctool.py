"""TOC tool: write a table of contents into the document between markers, and keep it fresh.

The toc module renders a contents; this puts one into the
document and, crucially, keeps it current without stacking a
new copy each time. The trick every doctoc-style tool needs
is a pair of markers, an opening and closing comment, that
fence the generated block, so the tool can find its own last
output and replace it rather than appending a second contents
below the first. So this looks for the markers: finding both,
it replaces everything between them with a freshly rendered
contents, which makes running it after every edit safe and
idempotent, the document converging on one accurate contents
rather than a museum of stale ones. Finding only the opening
marker, a placeholder a writer dropped where they want the
contents, it expands that line into the full fenced block.
Finding neither, it prepends a fresh block at the top, the
place a reader looks first. The contents itself is a bullet
list indented by heading depth, generated from the same
headings walk the rest of the outline tools read, so it
cannot disagree with them, and the generated bullets are not
themselves headings, so regenerating never mistakes the
contents for content and never lists itself. The whole thing
is operations, so the contents lives in the shared document
and every replica sees the same one, not a private overlay
one editor rendered and the others lack.
"""

from __future__ import annotations

from loom.author import Author
from loom.headings import headings
from loom.linewise import lines_of, visible_index
from loom.weave import Op, Weave

OPEN = "<!-- toc -->"
CLOSE = "<!-- /toc -->"


def _entries(weave: Weave) -> list[str]:
    found = headings(weave)
    if not found:
        return ["- (no headings yet)"]
    return [
        "  " * (heading.level - 1) + "- " + heading.title
        for heading in found
    ]


def _block(weave: Weave) -> str:
    return "\n".join([OPEN, *_entries(weave), CLOSE])


def _find(lines: list[str], marker: str, start: int = 0) -> int | None:
    for index in range(start, len(lines)):
        if lines[index].strip() == marker:
            return index
    return None


def _replace_region(
    author: Author, first: int, last: int, text: str
) -> list[Op]:
    lines = lines_of(author.weave)
    start = visible_index(author.weave, first, 0)
    end = visible_index(author.weave, last, len(lines[last]))
    ops = author.erase_at(start, end - start)
    ops.extend(author.type_at(start, text))
    return ops


def insert_toc(author: Author) -> list[Op]:
    lines = lines_of(author.weave)
    block = _block(author.weave)
    open_at = _find(lines, OPEN)
    close_at = (
        _find(lines, CLOSE, open_at + 1) if open_at is not None else None
    )
    if open_at is not None and close_at is not None:
        current = "\n".join(lines[open_at : close_at + 1])
        if current == block:
            return []
        return _replace_region(author, open_at, close_at, block)
    if open_at is not None:
        return _replace_region(author, open_at, open_at, block)
    return author.type_at(0, block + "\n\n")


def has_toc(weave: Weave) -> bool:
    lines = lines_of(weave)
    return _find(lines, OPEN) is not None and _find(lines, CLOSE) is not None
