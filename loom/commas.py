"""Commas: parse and render comma-separated values, quoting the fields that need it.

Tabular data arrives as CSV, and this reads and writes it by
the common rules: fields separated by commas, rows by
newlines, and a field that contains a comma, a quote, or a
newline wrapped in double quotes with any interior quote
doubled. Parsing is a state machine rather than a line split,
because a quoted field may hold a newline and splitting on
newlines first would tear such a field in two, the classic
CSV bug; the machine tracks whether it is inside quotes and
only a newline outside them ends a row. Rendering is the
inverse and quotes exactly the fields that would otherwise be
misread, leaving the plain ones bare so the output stays as
readable as the data allows, and parse and render round-trip:
feeding rendered rows back through the parser returns the same
rows. The scope is stated: the delimiter is the comma, not a
caller-chosen one, because a configurable delimiter is a
second format wearing the first's name and the comma is what
CSV means; carriage returns are tolerated and dropped so a
file saved on one platform reads on another; and a trailing
newline does not conjure a phantom empty row, since a file
that ends its last row with a newline meant to end the row,
not to add another. What it does not do is guess types: every
field comes back a string, because CSV carries no types and a
parser that inferred them would turn a zip code into a number
and lose its leading zero.
"""

from __future__ import annotations

QUOTE = '"'
SPECIAL = ',"\n'


def parse(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    in_quotes = False
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if in_quotes:
            if char == QUOTE:
                if index + 1 < length and text[index + 1] == QUOTE:
                    field.append(QUOTE)
                    index += 2
                    continue
                in_quotes = False
                index += 1
                continue
            field.append(char)
            index += 1
            continue
        if char == QUOTE:
            in_quotes = True
        elif char == ",":
            row.append("".join(field))
            field = []
        elif char == "\n":
            row.append("".join(field))
            rows.append(row)
            row = []
            field = []
        elif char != "\r":
            field.append(char)
        index += 1
    if field or row:
        row.append("".join(field))
        rows.append(row)
    return rows


def _quote(field: str) -> str:
    if any(char in field for char in SPECIAL):
        return QUOTE + field.replace(QUOTE, QUOTE + QUOTE) + QUOTE
    return field


def render(rows: list[list[str]]) -> str:
    return "\n".join(
        ",".join(_quote(field) for field in row) for row in rows
    )
