from __future__ import annotations

import pytest

from loom.author import Author
from loom.blockquotes import (
    quote_depth,
    quote_lines,
    quoted_lines,
    unquote_lines,
)
from loom.circle import Circle
from loom.errors import Missing


class TestDepth:
    def test_a_single_marker_is_depth_one(self):
        assert quote_depth("> quoted") == 1

    def test_nested_markers_add_depth(self):
        assert quote_depth(">> deep") == 2

    def test_unquoted_text_is_depth_zero(self):
        assert quote_depth("plain") == 0


class TestQuote:
    def test_quoting_marks_every_line_in_range(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb")
        quote_lines(author, 0, 1)
        assert author.text() == "> a\n> b"

    def test_quoting_marks_blank_lines_too(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\nb")
        quote_lines(author, 0, 2)
        assert author.text() == "> a\n> \n> b"


class TestUnquote:
    def test_unquoting_removes_one_marker(self):
        author = Author(site="alice")
        author.type_at(0, "> a\n> b")
        unquote_lines(author, 0, 1)
        assert author.text() == "a\nb"

    def test_unquoting_removes_only_one_level(self):
        author = Author(site="alice")
        author.type_at(0, ">> deep")
        unquote_lines(author, 0, 0)
        assert quote_depth(author.text()) == 1

    def test_unquoting_an_unmarked_line_does_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "plain")
        result = unquote_lines(author, 0, 0)
        assert result == []
        assert author.text() == "plain"


class TestReading:
    def test_quoted_lines_are_listed(self):
        author = Author(site="alice")
        author.type_at(0, "> yes\nno\n> also")
        assert quoted_lines(author) == {0, 2}


class TestGuards:
    def test_a_range_out_of_bounds_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "a")
        with pytest.raises(Missing):
            quote_lines(author, 0, 5)


class TestConvergence:
    def test_quoting_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "one\ntwo"),
        )
        circle.settle()
        circle.say("alice", quote_lines(circle.author("alice"), 0, 1))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "> one\n> two"
