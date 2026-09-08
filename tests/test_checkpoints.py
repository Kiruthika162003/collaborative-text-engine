from __future__ import annotations

import pytest

from loom.author import Author
from loom.checkpoints import Shelf
from loom.errors import Invalid, Missing
from loom.snapshot import same_fabric


def working_day() -> tuple[Author, Shelf]:
    author = Author(site="alice")
    shelf = Shelf()
    author.type_at(0, "the draft")
    shelf.keep("morning", author.weave)
    author.type_at(9, " grows longer")
    author.erase_at(0, 4)
    shelf.keep("evening", author.weave)
    return author, shelf


class TestTheShelf:
    def test_a_recalled_moment_is_the_whole_fabric(
        self,
    ):
        author, shelf = working_day()
        morning = shelf.recall("morning")
        assert morning.text() == "the draft"
        evening = shelf.recall("evening")
        assert same_fabric(evening, author.weave)

    def test_names_never_move(self):
        author, shelf = working_day()
        with pytest.raises(Invalid) as caught:
            shelf.keep("morning", author.weave)
        assert "slides while you sleep" in str(
            caught.value
        )

    def test_the_unshelved_names_what_it_does_hold(
        self,
    ):
        _author, shelf = working_day()
        with pytest.raises(Missing) as caught:
            shelf.recall("noon")
        message = str(caught.value)
        assert "'morning'" in message
        assert "'evening'" in message

    def test_a_nameless_moment_is_just_the_past(self):
        author, shelf = working_day()
        with pytest.raises(Invalid):
            shelf.keep("  ", author.weave)


class TestTheRoad:
    def test_the_road_counts_three_honest_verbs(self):
        _author, shelf = working_day()
        report = shelf.road("morning", "evening")
        assert (
            "5 glyph(s) kept, 13 added, 4 dropped"
        ) in report
        assert "reverses the verbs" in report

    def test_reversing_the_names_reverses_the_verbs(
        self,
    ):
        _author, shelf = working_day()
        back = shelf.road("evening", "morning")
        assert "13 dropped" in back
        assert "4 added" in back

    def test_a_recalled_moment_can_rejoin_the_living(
        self,
    ):
        _author, shelf = working_day()
        revived = Author(
            site="alice", weave=shelf.recall("morning")
        )
        for op_id in revived.weave.by_id:
            top = revived.clock.seen.get(
                op_id.site, 0
            )
            revived.clock.seen[op_id.site] = max(
                top, op_id.counter
            )
        revived.witness_rank = 50
        revived.type_at(0, "> ")
        assert revived.text() == "> the draft"


class TestListing:
    def test_the_day_in_the_order_it_happened(self):
        _author, shelf = working_day()
        page = shelf.listing()
        assert page.index("morning") < page.index(
            "evening"
        )

    def test_the_empty_shelf_admits_it(self):
        assert "no moment has been worth a name" in (
            Shelf().listing()
        )
