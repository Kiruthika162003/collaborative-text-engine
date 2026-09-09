"""A format day: a messy draft run through the tidying organs, one pass each.

A document arrives with trailing spaces, blank-line drifts,
mixed bullets, a misnumbered list, and an unaligned table, and
the formatting organs clean it in sequence: trim the trailing
whitespace, collapse the blank runs, unify the bullets,
renumber the list, align the table. Each is real operations on
one author, so the tidied document is the document, not a
rendering. Run with:
python -m examples.formatday
"""

from __future__ import annotations

from loom.author import Author
from loom.blanklines import collapse_blanks
from loom.bulletstyle import normalize_bullets
from loom.renumber import renumber
from loom.tableformat import format_tables
from loom.whitespace import trim_trailing

MESSY = (
    "# Title  \n"
    "\n"
    "\n"
    "* first  \n"
    "+ second\n"
    "\n"
    "1. a\n"
    "3. b\n"
    "\n"
    "|x|y|\n"
    "|-|-|\n"
    "|1|2|"
)


def main() -> int:
    author = Author(site="alice")
    author.type_at(0, MESSY)
    print("before:")
    print(author.text())

    trim_trailing(author)
    collapse_blanks(author, keep=1)
    normalize_bullets(author, "-")
    renumber(author)
    format_tables(author)

    print()
    print("after:")
    print(author.text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
