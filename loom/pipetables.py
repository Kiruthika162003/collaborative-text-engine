"""Pipe tables: the Markdown table read out of the text and rendered back aligned.

The grid module is a table as a data structure with row
ids; this is a table as text, the pipe-and-dash syntax a
Markdown writer types, parsed out of the visible cloth and
rendered back with its columns aligned. A block is a table
only if a header row of pipes is followed by a separator
row of dashes, because pipes alone are just prose about
plumbing and inventing a table around them corrupts the
text; the separator is the signature that says a table was
meant. Alignment is read from the colons in that separator,
left, right, or centre, and honoured when rendering, and
the column widths are measured with the display-width rule
rather than the glyph count, so a column holding a wide
glyph still lines up under a fixed-width font instead of
drifting one cell right per wide character. A ragged row,
one with fewer cells than the header, is padded to width
rather than dropped, because a row a collaborator half-typed
is data to keep, not an error to erase, and an over-long
row keeps its extra cells rather than truncating them, on
the same principle that the tool's job is to show what is
there, not to decide what should have been. Rendering is
idempotent on a table it parsed: feed its output back in
and the same table comes out, which is the property that
lets a formatter run on every save without churning the
document.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.columns import display_width
from loom.weave import Weave

SEPARATOR_CELL = re.compile(r"^:?-+:?$")


@dataclass(frozen=True)
class Table:
    headers: list[str]
    alignments: list[str]
    rows: list[list[str]]


def _split_row(line: str) -> list[str]:
    trimmed = line.strip()
    if trimmed.startswith("|"):
        trimmed = trimmed[1:]
    if trimmed.endswith("|"):
        trimmed = trimmed[:-1]
    return [cell.strip() for cell in trimmed.split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(
        SEPARATOR_CELL.match(cell) for cell in cells
    )


def _alignment(cell: str) -> str:
    left = cell.startswith(":")
    right = cell.endswith(":")
    if left and right:
        return "center"
    if right:
        return "right"
    if left:
        return "left"
    return "default"


def parse(block: str) -> Table | None:
    lines = block.split("\n")
    if len(lines) < 2:
        return None
    headers = _split_row(lines[0])
    separator = _split_row(lines[1])
    if not _is_separator(separator):
        return None
    alignments = [_alignment(cell) for cell in separator]
    rows = [_split_row(line) for line in lines[2:] if line.strip()]
    return Table(headers=headers, alignments=alignments, rows=rows)


def find_tables(weave: Weave) -> list[Table]:
    lines = weave.text().split("\n")
    found = []
    index = 0
    while index < len(lines) - 1:
        if _is_separator(_split_row(lines[index + 1])) and "|" in lines[
            index
        ]:
            end = index + 2
            while end < len(lines) and "|" in lines[end]:
                end += 1
            table = parse("\n".join(lines[index:end]))
            if table is not None:
                found.append(table)
            index = end
            continue
        index += 1
    return found


def _justify(cell: str, width: int, align: str) -> str:
    pad = width - display_width(cell)
    if pad <= 0:
        return cell
    if align == "right":
        return " " * pad + cell
    if align == "center":
        left = pad // 2
        return " " * left + cell + " " * (pad - left)
    return cell + " " * pad


def _widths(table: Table) -> list[int]:
    columns = len(table.headers)
    widths = [display_width(head) for head in table.headers]
    for row in table.rows:
        for index in range(columns):
            if index < len(row):
                widths[index] = max(widths[index], display_width(row[index]))
    return [max(width, 3) for width in widths]


def _separator_cell(width: int, align: str) -> str:
    if align == "center":
        return ":" + "-" * (width - 2) + ":"
    if align == "right":
        return "-" * (width - 1) + ":"
    if align == "left":
        return ":" + "-" * (width - 1)
    return "-" * width


def render(table: Table) -> str:
    widths = _widths(table)
    columns = len(table.headers)
    lines = [
        "| "
        + " | ".join(
            _justify(table.headers[index], widths[index], "default")
            for index in range(columns)
        )
        + " |"
    ]
    lines.append(
        "| "
        + " | ".join(
            _separator_cell(widths[index], table.alignments[index])
            for index in range(columns)
        )
        + " |"
    )
    for row in table.rows:
        cells = [
            row[index] if index < len(row) else ""
            for index in range(columns)
        ]
        extra = row[columns:]
        rendered = " | ".join(
            _justify(cells[index], widths[index], table.alignments[index])
            for index in range(columns)
        )
        if extra:
            rendered += " | " + " | ".join(extra)
        lines.append("| " + rendered + " |")
    return "\n".join(lines)
