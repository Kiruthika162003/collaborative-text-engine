"""Table transform: convert between CSV and Markdown tables, the two shapes tabular data wears.

Data lives as CSV when a spreadsheet made it and as a
Markdown table when a document holds it, and a writer pasting
one into the other wants the conversion done. This bridges the
two by borrowing both readers: CSV in through the commas
parser, out through the pipetables renderer, and back the same
way. The one convention it commits to is that a table's first
row is its header, because Markdown tables have a header row
and CSV does not distinguish one, and treating the first CSV
row as the header is what a reader means nine times in ten;
this is stated rather than hidden so a caller with headerless
data knows to prepend a header row or expect its first data
row promoted. Alignment does not survive the trip to CSV,
because CSV has no notion of a column aligned right or centre,
so a Markdown table converted to CSV and back comes home
left-aligned, which is honest loss rather than a silent
guess at alignments the CSV never carried. Everything else
round-trips through the trim the renderers apply, so a CSV
turned into a table and back returns its fields with their
surrounding spaces normalized, which is the tables' doing and
named here so it is expected rather than surprising.
"""

from __future__ import annotations

from loom.commas import parse as csv_parse
from loom.commas import render as csv_render
from loom.pipetables import Table
from loom.pipetables import parse as table_parse
from loom.pipetables import render as table_render


def csv_to_pipes(csv_text: str) -> str:
    rows = csv_parse(csv_text)
    if not rows:
        return ""
    headers = rows[0]
    table = Table(
        headers=headers,
        alignments=["default"] * len(headers),
        rows=rows[1:],
    )
    return table_render(table)


def pipes_to_csv(markdown_text: str) -> str:
    table = table_parse(markdown_text)
    if table is None:
        return ""
    return csv_render([table.headers, *table.rows])
