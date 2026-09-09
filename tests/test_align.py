from __future__ import annotations

import pytest

from loom.align import align, aligned_column
from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid, Missing


class TestAlign:
    def test_delimiters_line_up_in_a_column(self):
        author = Author(site="alice")
        author.type_at(0, "a = 1\nbb = 2\nccc = 3")
        align(author, 0, 2, "=")
        assert author.text() == "a   = 1\nbb  = 2\nccc = 3"

    def test_an_aligned_block_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "aa = 1\nbb = 2")
        assert align(author, 0, 1, "=") == []

    def test_a_line_without_the_delimiter_is_left_alone(self):
        author = Author(site="alice")
        author.type_at(0, "a = 1\nno delimiter here\nbb = 2")
        align(author, 0, 2, "=")
        assert "no delimiter here" in author.text()

    def test_no_delimiter_anywhere_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "plain\nlines\nhere")
        assert align(author, 0, 2, "=") == []


class TestQueriesAndGuards:
    def test_aligned_column_reports_the_target(self):
        author = Author(site="alice")
        author.type_at(0, "a = 1\nccc = 3")
        assert aligned_column(author, 0, 1, "=") == 4

    def test_an_empty_delimiter_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "a = 1")
        with pytest.raises(Invalid):
            align(author, 0, 0, "")

    def test_a_range_out_of_bounds_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "a = 1")
        with pytest.raises(Missing):
            align(author, 0, 9, "=")


class TestConvergence:
    def test_alignment_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "x = 1\nyy = 2"),
        )
        circle.settle()
        circle.say("alice", align(circle.author("alice"), 0, 1, "="))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "x  = 1\nyy = 2"
