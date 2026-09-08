from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid, Missing
from loom.splice import splice_at, swap_word


class TestTheSeam:
    def test_replace_reads_as_one_thought(self):
        author = Author(site="alice")
        author.type_at(0, "the quick fox")
        splice_at(author, 4, 5, "swift")
        assert author.text() == "the swift fox"

    def test_pure_insertion_and_pure_removal(self):
        author = Author(site="alice")
        author.type_at(0, "ab")
        splice_at(author, 1, 0, "-")
        assert author.text() == "a-b"
        splice_at(author, 1, 1, "")
        assert author.text() == "ab"

    def test_nothing_over_nothing_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "x")
        with pytest.raises(Invalid) as caught:
            splice_at(author, 0, 0, "")
        assert "no thought in it" in str(caught.value)
        with pytest.raises(Invalid):
            splice_at(author, 0, -1, "y")

    def test_the_replacement_anchors_left_of_the_dead(
        self,
    ):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(
                0, "the quick fox"
            ),
        )
        circle.settle()
        extension = circle.author("bob").type_at(
            9, "er"
        )
        swap = splice_at(
            circle.author("alice"), 4, 5, "swift"
        )
        circle.say("bob", extension)
        circle.say("alice", swap)
        circle.settle()
        assert circle.converged() == "the swifter fox"


class TestWordSwap:
    def test_the_first_occurrence_is_the_one_swapped(
        self,
    ):
        author = Author(site="alice")
        author.type_at(0, "fox and fox")
        swap_word(author, "fox", "owl")
        assert author.text() == "owl and fox"

    def test_an_unsaid_word_cannot_be_swapped(self):
        author = Author(site="alice")
        author.type_at(0, "plain cloth")
        with pytest.raises(Missing) as caught:
            swap_word(author, "velvet", "silk")
        assert "the cloth does not say" in str(
            caught.value
        )

    def test_the_empty_word_matches_nothing_useful(self):
        author = Author(site="alice")
        author.type_at(0, "x")
        with pytest.raises(Invalid):
            swap_word(author, "", "y")
