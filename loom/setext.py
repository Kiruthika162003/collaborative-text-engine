"""Setext headings: convert the underlined heading style to the hash style, as operations.

Markdown has two heading styles, the hash prefix and the
setext underline, a line of text with a row of equals or
dashes beneath it, and a document that mixes them reads
inconsistently and defeats the outline tools that look for
hashes. This normalizes the underlined ones into hash
headings: a title underlined with equals becomes a level-one
hash heading, a title underlined with dashes a level-two,
which is exactly the mapping the setext convention assigns.
The conversion is operations, shearing the underline row and
the newline joining it to its title and prefixing the title
with its hashes, so every replica ends with the same
normalized heading rather than one screen showing hashes and
another underlines. Two false friends are avoided on purpose.
A row of dashes with no text line above it is a thematic
break, a horizontal rule, not a heading underline, so it is
left alone because it underlines nothing. And a single dash
is not treated as an underline at all, requiring at least two
so a title that happens to sit above a one-dash list bullet
is not swept into a heading it was never meant to be. The
conversions apply from the bottom of the document upward, so
merging a title and its underline into one line, which
shortens the document, never shifts the line numbers of a
heading still waiting above it.
"""

from __future__ import annotations

from loom.author import Author
from loom.linewise import lines_of, visible_index
from loom.weave import Op


def _is_underline(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 2:
        return False
    return all(char == "=" for char in stripped) or all(
        char == "-" for char in stripped
    )


def _pairs(lines: list[str]) -> list[tuple[int, int]]:
    pairs = []
    index = 0
    while index < len(lines) - 1:
        title = lines[index]
        under = lines[index + 1]
        if title.strip() and _is_underline(under):
            level = 1 if under.strip()[0] == "=" else 2
            pairs.append((index, level))
            index += 2
        else:
            index += 1
    return pairs


def setext_headings(author: Author) -> list[tuple[int, int]]:
    return _pairs(lines_of(author.weave))


def to_atx(author: Author) -> list[Op]:
    pairs = _pairs(lines_of(author.weave))
    ops: list[Op] = []
    for title_line, level in reversed(pairs):
        lines = lines_of(author.weave)
        title_length = len(lines[title_line])
        underline_length = len(lines[title_line + 1])
        start = visible_index(author.weave, title_line, title_length)
        ops.extend(author.erase_at(start, 1 + underline_length))
        marker = "# " if level == 1 else "## "
        ops.extend(
            author.type_at(visible_index(author.weave, title_line, 0), marker)
        )
    return ops
