from __future__ import annotations

from loom.linediff import added, changed, line_ops, removed, render


class TestLineOps:
    def test_a_changed_line_shows_removed_then_added(self):
        assert line_ops("a\nb\nc", "a\nB\nc") == [
            (" ", "a"),
            ("-", "b"),
            ("+", "B"),
            (" ", "c"),
        ]

    def test_an_added_line_is_a_plus(self):
        assert line_ops("a", "a\nb") == [(" ", "a"), ("+", "b")]

    def test_a_removed_line_is_a_minus(self):
        assert line_ops("a\nb", "a") == [(" ", "a"), ("-", "b")]

    def test_identical_text_is_all_context(self):
        assert all(mark == " " for mark, _line in line_ops("x\ny", "x\ny"))


class TestRender:
    def test_render_marks_each_line(self):
        assert render("a\nb", "a\nB") == " a\n-b\n+B"


class TestCounts:
    def test_added_and_removed_are_counted(self):
        assert added("a\nb", "a\nb\nc\nd") == 2
        assert removed("a\nb\nc", "a") == 2

    def test_changed_detects_a_difference(self):
        assert changed("a", "b")
        assert not changed("same", "same")
