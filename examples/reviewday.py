"""A review day: the editor reads, marks, strikes, and signs the ledger.

A draft arrives, the editor checkpoints it, dresses a
phrase for emphasis, swaps a weak word, strikes a
redundancy, and the day closes with every instrument
reporting: the redline against the arrival, the spans
with their dress, the byline with both hands, and the
prose numbers of what survived. Run with:
python -m examples.reviewday
"""

from __future__ import annotations

from loom.attribution import byline
from loom.checkpoints import Shelf
from loom.circle import Circle
from loom.marks import Mark, Wardrobe
from loom.prose import word_count
from loom.redlines import render
from loom.splice import swap_word


def main() -> int:
    circle = Circle.of(["writer", "editor"])
    writer = circle.author("writer")
    editor = circle.author("editor")
    circle.say(
        "writer",
        writer.type_at(
            0, "the very good draft is very done"
        ),
    )
    circle.settle()

    shelf = Shelf()
    shelf.keep("arrival", editor.weave)
    print("arrive:  draft checkpointed by the editor")

    wardrobe = Wardrobe(weave=editor.weave)
    strands = [
        editor.weave.strand_at_visible(index).id
        for index in range(4, 13)
    ]
    wardrobe.dress(
        Mark(
            id=editor._mint(),
            style="emphasis",
            start=strands[0],
            end=strands[-1],
        )
    )
    print("dress:   'very good' wears emphasis")

    circle.say(
        "editor", swap_word(editor, "good", "strong")
    )
    circle.say(
        "editor", editor.erase_at(24, 5)
    )
    circle.settle()
    print(f"text:    {circle.converged()!r}")

    print()
    print("redline against arrival:")
    print(
        render(editor.weave, shelf.recall("arrival"))
    )
    print()
    runs = byline(editor.weave)
    print(
        "byline:  "
        + "; ".join(
            f"{site}: {text!r}"
            for text, site in runs
        )
    )
    print(
        f"words:   {word_count(editor.weave)} "
        "surviving"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
