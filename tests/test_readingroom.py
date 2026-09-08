from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid
from loom.readingroom import (
    census,
    count,
    current_position,
    find,
    still_says,
)


def foxy_author() -> Author:
    author = Author(site="alice")
    author.type_at(0, "the fox met the fox")
    return author


class TestFinding:
    def test_every_occurrence_gets_a_bookmark(self):
        author = foxy_author()
        marks = find(author.weave, "fox")
        assert len(marks) == 2
        assert marks[0].found_at == 4
        assert marks[1].found_at == 16

    def test_overlaps_are_counted_honestly(self):
        author = Author(site="alice")
        author.type_at(0, "aaa")
        assert count(author.weave, "aa") == 2
        assert "twice to anyone who actually looks" in (
            census(author.weave, "aa")
        )

    def test_the_dead_are_unsearchable(self):
        author = foxy_author()
        author.erase_at(4, 3)
        assert count(author.weave, "fox") == 1

    def test_the_empty_needle_is_refused(self):
        author = foxy_author()
        with pytest.raises(Invalid):
            find(author.weave, "")


class TestBookmarks:
    def test_pins_survive_upstream_typing(self):
        author = foxy_author()
        mark = find(author.weave, "fox")[0]
        author.type_at(0, ">>> ")
        assert still_says(author.weave, mark, "fox")
        assert (
            current_position(author.weave, mark) == 8
        )

    def test_an_edit_inside_turns_match_to_near_miss(
        self,
    ):
        author = foxy_author()
        mark = find(author.weave, "fox")[0]
        author.erase_at(5, 1)
        assert not still_says(
            author.weave, mark, "fox"
        )

    def test_typing_inside_the_stretch_is_also_honest(
        self,
    ):
        author = foxy_author()
        mark = find(author.weave, "fox")[0]
        author.type_at(5, "l")
        assert not still_says(
            author.weave, mark, "fox"
        )
        assert still_says(author.weave, mark, "flox")
