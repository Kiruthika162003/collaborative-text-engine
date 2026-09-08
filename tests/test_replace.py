from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid
from loom.replace import replace_all


class TestReplacing:
    def test_every_occurrence_is_rewritten(self):
        author = Author(site="alice")
        author.type_at(0, "the cat sat on the cat mat")
        result = replace_all(author, "cat", "dog")
        assert result.occurrences == 2
        assert author.text() == (
            "the dog sat on the dog mat"
        )

    def test_a_growing_replacement_works(self):
        author = Author(site="alice")
        author.type_at(0, "aaa")
        replace_all(author, "a", "bb")
        assert author.text() == "bbbbbb"

    def test_replacement_with_empty_deletes(self):
        author = Author(site="alice")
        author.type_at(0, "remove me please")
        result = replace_all(author, "remove ", "")
        assert result.occurrences == 1
        assert author.text() == "me please"

    def test_a_missing_term_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "nothing here")
        result = replace_all(author, "absent", "x")
        assert result.occurrences == 0
        assert result.ops == []

    def test_an_empty_needle_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "text")
        with pytest.raises(Invalid):
            replace_all(author, "", "x")

    def test_replacing_a_term_with_itself_is_refused(
        self,
    ):
        author = Author(site="alice")
        author.type_at(0, "same")
        with pytest.raises(Invalid):
            replace_all(author, "same", "same")


class TestConvergence:
    def test_replace_operations_converge_on_a_peer(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(
                0, "cat and cat"
            ),
        )
        circle.settle()
        result = replace_all(
            circle.author("alice"), "cat", "owl"
        )
        circle.say("alice", result.ops)
        circle.settle()
        assert circle.converged() == "owl and owl"
