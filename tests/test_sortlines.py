from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Missing
from loom.sortlines import is_sorted, sort_lines


class TestSort:
    def test_a_block_is_sorted_in_place(self):
        author = Author(site="alice")
        author.type_at(0, "c\na\nb\nd")
        sort_lines(author, 0, 2)
        assert author.text() == "a\nb\nc\nd"

    def test_lines_outside_the_range_are_untouched(self):
        author = Author(site="alice")
        author.type_at(0, "z\nc\na\nb")
        sort_lines(author, 1, 3)
        assert author.text() == "z\na\nb\nc"

    def test_reverse_sorts_descending(self):
        author = Author(site="alice")
        author.type_at(0, "a\nc\nb")
        sort_lines(author, 0, 2, reverse=True)
        assert author.text() == "c\nb\na"


class TestNoop:
    def test_an_already_sorted_block_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb\nc")
        assert sort_lines(author, 0, 2) == []

    def test_is_sorted_reports_order(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb\nc")
        assert is_sorted(author, 0, 2)
        assert not is_sorted(author, 0, 2, reverse=True)


class TestGuards:
    def test_a_range_out_of_bounds_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb")
        with pytest.raises(Missing):
            sort_lines(author, 0, 9)


class TestConvergence:
    def test_a_sort_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "banana\napple\ncherry"),
        )
        circle.settle()
        circle.say("alice", sort_lines(circle.author("alice"), 0, 2))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "apple\nbanana\ncherry"
