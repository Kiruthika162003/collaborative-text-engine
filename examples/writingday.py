"""A writing day: one author drafts, and the reading organs read along.

A solo writer drafts a short structured note, and the
loom's reading tools narrate the work as it stands: the
heading outline, the list renumbered, the paragraph count,
the concordance's most-leaned-on word, the links found,
and the prose numbers. No network, no second hand, just a
document watching itself take shape. Run with:
python -m examples.writingday
"""

from __future__ import annotations

from loom.concordance import top
from loom.headings import outline
from loom.library import Library
from loom.links import detect
from loom.lists import render as render_list
from loom.paragraphs import block_count
from loom.prose import word_count


def main() -> int:
    library = Library(site="writer")
    library.open_doc("notes")
    note = (
        "# Trip Plan\n\n"
        "the plan is simple and the plan is firm\n\n"
        "## Packing\n"
        "1. tent\n"
        "5. stove\n"
        "9. maps\n\n"
        "see https://trails.example for the route"
    )
    library.type_in("notes", 0, note)
    weave = library.docs["notes"].author.weave

    print("outline:")
    print(outline(weave))
    print()
    print("packing list:")
    print(render_list(weave))
    print()
    print(f"paragraphs: {block_count(weave)}")
    leaned = top(weave, 1)[0]
    print(
        f"most-used:  {leaned[0]!r} x{leaned[1]}"
    )
    print(
        f"links:      {len(detect(weave))} found"
    )
    print(f"words:      {word_count(weave)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
