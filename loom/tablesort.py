"""Table sort: reorder a Markdown table's rows by a column, numeric or textual, as operations.

Sorting a table by one of its columns is a common gesture, and
this does it by parsing the table, reordering its rows, and
rendering it back, all as a patch so only what moved changes.
The one decision that matters is how to compare a column, and
it is made from the data rather than imposed: if every cell in
the sort column is a number the rows sort numerically, so ten
follows nine rather than preceding it as it would by text, and
otherwise they sort as text. That check is per column and per
call, because the same table has a numeric column and a textual
one and the right comparison depends on which the caller chose,
and guessing one for the whole table would sort the other
wrong. A cell missing from a short row sorts as empty, which
puts a ragged row at one end rather than crashing on the absent
column, keeping with the table modules' habit of tolerating
raggedness rather than refusing it. The header and the
alignment row are never sorted, since they are the table's
frame and not its data, and every table in the document is
sorted by the same column index, which is what a caller asking
to sort by the second column of their tables means. It patches,
so it converges and touches only the rows that actually moved,
and a table already in order produces no operations at all.
"""

from __future__ import annotations

from loom.author import Author
from loom.patch import patch
from loom.pipetables import Table, _is_separator, _split_row, parse, render
from loom.weave import Op


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def _sort_rows(table: Table, column: int, reverse: bool) -> Table:
    def cell(row: list[str]) -> str:
        return row[column] if column < len(row) else ""

    cells = [cell(row) for row in table.rows]
    numeric = bool(cells) and all(_is_number(value) for value in cells)
    if numeric:
        rows = sorted(table.rows, key=lambda row: float(cell(row)), reverse=reverse)
    else:
        rows = sorted(table.rows, key=cell, reverse=reverse)
    return Table(
        headers=table.headers, alignments=table.alignments, rows=rows
    )


def _rebuild(text: str, column: int, reverse: bool) -> str:
    lines = text.split("\n")
    out: list[str] = []
    index = 0
    while index < len(lines):
        if (
            index + 1 < len(lines)
            and "|" in lines[index]
            and _is_separator(_split_row(lines[index + 1]))
        ):
            end = index + 2
            while end < len(lines) and "|" in lines[end]:
                end += 1
            table = parse("\n".join(lines[index:end]))
            if table is not None:
                out.append(render(_sort_rows(table, column, reverse)))
                index = end
                continue
        out.append(lines[index])
        index += 1
    return "\n".join(out)


def sort_table(
    author: Author, column: int, reverse: bool = False
) -> list[Op]:
    return patch(author, _rebuild(author.text(), column, reverse))
