from __future__ import annotations

from loom.author import Author
from loom.checkpoints import Shelf
from loom.circle import Circle
from loom.redlines import render


def reviewed_pair() -> tuple[Circle, Shelf]:
    circle = Circle.of(["alice", "bob"])
    circle.say(
        "alice",
        circle.author("alice").type_at(
            0, "the draft stands"
        ),
    )
    circle.settle()
    shelf = Shelf()
    shelf.keep(
        "sent-for-review",
        circle.author("alice").weave,
    )
    circle.say(
        "bob",
        circle.author("bob").type_at(9, " now"),
    )
    circle.say(
        "bob", circle.author("bob").erase_at(0, 4)
    )
    circle.settle()
    return circle, shelf


class TestTheRedline:
    def test_changes_wear_their_hands(self):
        circle, shelf = reviewed_pair()
        page = render(
            circle.author("alice").weave,
            shelf.recall("sent-for-review"),
        )
        assert page.splitlines()[0] == (
            "[-the -]draft[+ now+ bob] stands"
        )
        assert "bob added 4 glyph(s)" in page
        assert (
            "alice's baseline text lost 4 glyph(s)"
        ) in page

    def test_silent_churn_is_totaled_not_woven(self):
        author = Author(site="alice")
        author.type_at(0, "keep")
        shelf = Shelf()
        shelf.keep("base", author.weave)
        author.type_at(4, " temp")
        author.erase_at(4, 5)
        page = render(
            author.weave, shelf.recall("base")
        )
        assert "[+" not in page.split("\n")[0]
        assert (
            "5 glyph(s) of silent churn"
        ) in page

    def test_no_changes_is_said_plainly(self):
        author = Author(site="alice")
        author.type_at(0, "still")
        shelf = Shelf()
        shelf.keep("base", author.weave)
        page = render(
            author.weave, shelf.recall("base")
        )
        assert (
            "no changes; the baseline is the fabric"
        ) in page
