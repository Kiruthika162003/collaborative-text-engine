from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid
from loom.undo import Scribe


def solo_scribe() -> Scribe:
    return Scribe(author=Author(site="alice"))


class TestUnsaying:
    def test_undo_of_typing_shears_what_it_wove(self):
        scribe = solo_scribe()
        scribe.type_at(0, "hello")
        scribe.type_at(5, " world")
        scribe.undo()
        assert scribe.author.text() == "hello"

    def test_undo_of_erasure_resurrects_in_place(self):
        scribe = solo_scribe()
        scribe.type_at(0, "hello world")
        scribe.erase_at(5, 6)
        assert scribe.author.text() == "hello"
        scribe.undo()
        assert scribe.author.text() == "hello world"

    def test_resurrection_survives_a_changed_district(
        self,
    ):
        scribe = solo_scribe()
        scribe.type_at(0, "abcd")
        scribe.erase_at(1, 2)
        scribe.type_at(1, "Z")
        scribe.undo()
        scribe.undo()
        assert scribe.author.text() == "abcd"

    def test_an_empty_stack_has_nothing_to_take_back(
        self,
    ):
        with pytest.raises(Invalid) as caught:
            solo_scribe().undo()
        assert "only unsay what it said" in str(
            caught.value
        )


class TestRedo:
    def test_redo_follows_undo_like_echo(self):
        scribe = solo_scribe()
        scribe.type_at(0, "draft")
        scribe.undo()
        assert scribe.author.text() == ""
        scribe.redo()
        assert scribe.author.text() == "draft"

    def test_redo_without_undo_is_refused(self):
        scribe = solo_scribe()
        scribe.type_at(0, "x")
        with pytest.raises(Invalid):
            scribe.redo()

    def test_a_new_gesture_burns_the_redo_pile(self):
        scribe = solo_scribe()
        scribe.type_at(0, "one")
        scribe.undo()
        scribe.type_at(0, "two")
        with pytest.raises(Invalid):
            scribe.redo()
        assert "0 unsaid" in scribe.history_page()


class TestSharedUnsaying:
    def test_an_undo_is_ordinary_operations_abroad(self):
        circle = Circle.of(["alice", "bob"])
        scribe = Scribe(author=circle.author("alice"))
        circle.say("alice", scribe.type_at(0, "oops"))
        circle.settle()
        assert circle.converged() == "oops"
        circle.say("alice", scribe.undo())
        circle.settle()
        assert circle.converged() == ""

    def test_undoing_under_a_concurrent_shear_is_calm(
        self,
    ):
        circle = Circle.of(["alice", "bob"])
        scribe = Scribe(author=circle.author("alice"))
        circle.say("alice", scribe.type_at(0, "ab"))
        circle.settle()
        bob_shears = circle.author("bob").erase_at(0, 1)
        circle.say("bob", bob_shears)
        undo_ops = scribe.undo()
        circle.say("alice", undo_ops)
        circle.settle()
        assert circle.converged() == ""
