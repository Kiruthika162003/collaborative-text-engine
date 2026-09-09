"""An export day: a draft tidied, numbered, analysed, and rendered to an HTML page.

A guide is drafted, tidied by the safe formatters, its
headings numbered, then read for readability and rendered to a
standalone HTML page ready to serve. Every step is real
operations on one author until the render, which reads the
finished text. Run with:
python -m examples.exportday
"""

from __future__ import annotations

from loom.author import Author
from loom.headings import outline
from loom.htmlpage import page
from loom.mdlint import clean
from loom.readability import flesch_reading_ease
from loom.sectionnumbers import number_headings
from loom.tidy import tidy

DRAFT = (
    "# Guide  \n"
    "\n"
    "\n"
    "A short intro to the thing.\n"
    "\n"
    "## Setup\n"
    "\n"
    "* clone it\n"
    "+ build it\n"
    "\n"
    "## Usage\n"
    "\n"
    "Run the command and read the output.\n"
)


def main() -> int:
    author = Author(site="alice")
    author.type_at(0, DRAFT)

    tidy(author)
    number_headings(author)

    print("outline:")
    print(outline(author.weave))
    print()
    print(f"clean:   {clean(author)}")
    print(f"ease:    {flesch_reading_ease(author.weave)}")

    print()
    print("html:")
    rendered = page(author.text())
    print(rendered.splitlines()[0])
    print(rendered.splitlines()[1])
    for line in rendered.splitlines():
        if line.startswith("<h1>"):
            print(line)
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
