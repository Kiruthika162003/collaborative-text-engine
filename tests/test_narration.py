from __future__ import annotations

from loom.author import Author
from loom.ids import OpId
from loom.marks import Mark, Wardrobe
from loom.narration import (
    announcements,
    narrate,
    plain_line,
    structure,
)


def dressed() -> Wardrobe:
    author = Author(site="alice")
    ops = author.type_at(0, "plain bold plain")
    wardrobe = Wardrobe(weave=author.weave)
    wardrobe.dress(
        Mark(
            id=OpId(site="alice", counter=100),
            style="bold",
            start=ops[6].id,
            end=ops[9].id,
        )
    )
    return wardrobe


class TestNarration:
    def test_formatting_is_announced_in_words(self):
        page = narrate(dressed())
        assert "[bold start] bold [bold end]" in page

    def test_plain_prose_gets_no_announcements(self):
        author = Author(site="alice")
        author.type_at(0, "nothing dressed")
        wardrobe = Wardrobe(weave=author.weave)
        assert narrate(wardrobe) == "nothing dressed"
        assert announcements(wardrobe) == 0

    def test_announcements_come_in_pairs(self):
        assert announcements(dressed()) == 2

    def test_the_plain_line_drops_all_marks(self):
        assert plain_line(dressed()) == (
            "plain bold plain"
        )


class TestStructure:
    def test_headings_and_items_are_announced(self):
        author = Author(site="alice")
        author.type_at(
            0, "# Title\n- one\n- two"
        )
        wardrobe = Wardrobe(weave=author.weave)
        page = structure(wardrobe)
        assert "(heading level 1) Title" in page
        assert "(item) one" in page
        assert "(item) two" in page

    def test_flat_prose_announces_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "just a sentence")
        wardrobe = Wardrobe(weave=author.weave)
        assert "nothing to announce" in structure(
            wardrobe
        )
