from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid, Missing
from loom.indent import indent_lines, outdent_lines


class TestIndent:
    def test_indent_shifts_every_line_in_range(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb\nc")
        indent_lines(author, 0, 2)
        assert author.text() == "  a\n  b\n  c"

    def test_indent_leaves_blank_lines_alone(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\nb")
        indent_lines(author, 0, 2)
        assert author.text() == "  a\n\n  b"

    def test_a_custom_unit_is_used(self):
        author = Author(site="alice")
        author.type_at(0, "x")
        indent_lines(author, 0, 0, unit="\t")
        assert author.text() == "\tx"


class TestOutdent:
    def test_outdent_removes_up_to_one_unit(self):
        author = Author(site="alice")
        author.type_at(0, "    a\n  b\nc")
        outdent_lines(author, 0, 2)
        assert author.text() == "  a\nb\nc"

    def test_outdent_takes_what_is_there_when_less_than_a_unit(self):
        author = Author(site="alice")
        author.type_at(0, " x")
        outdent_lines(author, 0, 0)
        assert author.text() == "x"

    def test_outdent_never_eats_a_non_space_glyph(self):
        author = Author(site="alice")
        author.type_at(0, "no indent")
        outdent_lines(author, 0, 0)
        assert author.text() == "no indent"


class TestGuards:
    def test_a_unit_of_letters_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "a")
        with pytest.raises(Invalid):
            indent_lines(author, 0, 0, unit="ab")

    def test_an_empty_unit_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "a")
        with pytest.raises(Invalid):
            indent_lines(author, 0, 0, unit="")

    def test_a_range_out_of_bounds_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb")
        with pytest.raises(Missing):
            indent_lines(author, 0, 9)


class TestConvergence:
    def test_an_indent_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "one\ntwo"),
        )
        circle.settle()
        circle.say(
            "alice", indent_lines(circle.author("alice"), 0, 1)
        )
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "  one\n  two"
