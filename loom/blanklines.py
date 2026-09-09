"""Blank lines: collapse runs of empty lines to a maximum, sparing code fences.

Documents accrete blank lines, three and four in a row where
one was meant, and this collapses those runs to a chosen
maximum, one by default, as operations woven through the
patch so only the surplus blanks are sheared and the rest of
the text keeps its strands. The one place it does not touch is
inside a fenced code block, where a run of blank lines is part
of the code and collapsing it would change what the code says;
this borrows the fences module to know which lines are code
and steps around them, so a shell script with a deliberate
double blank keeps it while the prose around the fence is
tidied. The maximum is the caller's, because one editor's
house style allows a single blank between paragraphs and
another allows two around headings, and a collapser that
imposed one number would fight half its users. A document
already within the limit mints nothing, the patch finding no
surplus to remove, so this too can run on every save without
churn. It collapses blank runs but never removes the last
newline or joins two paragraphs into one, because the job is
to remove excess space, not to reflow the document, and a
collapser that ran two paragraphs together would have
overstepped from tidying into rewriting.
"""

from __future__ import annotations

from loom.author import Author
from loom.fences import code_lines
from loom.patch import patch
from loom.weave import Op


def _collapse(author: Author, keep: int) -> str:
    lines = author.text().split("\n")
    code = code_lines(author.weave)
    out: list[str] = []
    blank_run = 0
    for index, line in enumerate(lines):
        if line.strip() == "" and index not in code:
            blank_run += 1
            if blank_run <= keep:
                out.append(line)
        else:
            blank_run = 0
            out.append(line)
    return "\n".join(out)


def collapse_blanks(author: Author, keep: int = 1) -> list[Op]:
    return patch(author, _collapse(author, keep))
