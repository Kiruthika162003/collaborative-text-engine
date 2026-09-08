from __future__ import annotations

import pytest

from loom.author import Author
from loom.cursors import Parlor
from loom.errors import Missing


def seated() -> tuple[Author, Parlor]:
    author = Author(site="alice")
    author.type_at(0, "hello world")
    parlor = Parlor(weave=author.weave)
    return author, parlor


class TestPlaces:
    def test_a_caret_reads_back_where_placed(self):
        _author, parlor = seated()
        parlor.place("bob", 5)
        assert parlor.visible_position("bob") == 5
        assert parlor.glyph_touched("bob") == "'o'"

    def test_the_head_is_position_zero(self):
        _author, parlor = seated()
        parlor.place("bob", 0)
        assert parlor.visible_position("bob") == 0
        assert parlor.glyph_touched("bob") == (
            "(the head)"
        )

    def test_upstream_typing_shifts_the_caret_right(
        self,
    ):
        author, parlor = seated()
        parlor.place("bob", 5)
        author.type_at(0, ">> ")
        assert parlor.visible_position("bob") == 8

    def test_downstream_typing_leaves_it_alone(self):
        author, parlor = seated()
        parlor.place("bob", 5)
        author.type_at(11, "!!!")
        assert parlor.visible_position("bob") == 5

    def test_a_sheared_anchor_holds_its_funeral_seat(
        self,
    ):
        author, parlor = seated()
        parlor.place("bob", 5)
        author.erase_at(2, 3)
        assert parlor.visible_position("bob") == 2
        author.type_at(0, "x")
        assert parlor.visible_position("bob") == 3


class TestTheParlor:
    def test_one_hand_one_place(self):
        _author, parlor = seated()
        parlor.place("bob", 2)
        parlor.place("bob", 7)
        assert parlor.visible_position("bob") == 7
        assert len(parlor.carets) == 1

    def test_parking_releases_the_place(self):
        _author, parlor = seated()
        parlor.place("bob", 2)
        assert "released" in parlor.park("bob")
        with pytest.raises(Missing):
            parlor.visible_position("bob")

    def test_the_roster_reads_aloud(self):
        _author, parlor = seated()
        parlor.place("bob", 5)
        parlor.place("cara", 0)
        page = parlor.roster()
        assert "2 caret(s) in the parlor:" in page
        assert "bob at 5, touching 'o'" in page
        assert "cara at 0, touching (the head)" in page

    def test_the_empty_parlor_says_so(self):
        _author, parlor = seated()
        assert "nobody is holding a place" in (
            parlor.roster()
        )
