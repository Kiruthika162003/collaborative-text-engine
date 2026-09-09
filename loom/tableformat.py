"""Table format: find the Markdown tables in a document and reformat them aligned, in place.

The pipetables module parses a table into a structure and
renders one back aligned; this closes the loop, finding the
tables inside a living document and replacing each with its
tidied form as operations. It walks the lines, and where a
header row is followed by a separator it takes the block
through the parser and the renderer and emits the aligned
result in that block's place, passing every non-table line
through untouched. The rebuilt document is applied as a
patch, so only the whitespace the alignment changed is woven,
the cell contents keeping their strands, and it converges
across replicas the way a patch does. Because the renderer is
idempotent on a table it parsed, formatting a document whose
tables are already tidy mints nothing, which lets a formatter
run on every save without churn. The definition of a table is
the pipetables one and inherits its honesty: a block is a
table only when a separator row follows the header, so a
paragraph that merely contains pipes is left as the prose it
is rather than mangled into a grid it never was.
"""

from __future__ import annotations

from loom.author import Author
from loom.patch import patch
from loom.pipetables import _is_separator, _split_row, parse, render
from loom.weave import Op


def _rebuild(text: str) -> str:
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
                out.append(render(table))
                index = end
                continue
        out.append(lines[index])
        index += 1
    return "\n".join(out)


def format_tables(author: Author) -> list[Op]:
    return patch(author, _rebuild(author.text()))


def formatted_text(text: str) -> str:
    return _rebuild(text)
