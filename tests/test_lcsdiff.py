from __future__ import annotations

from loom.lcsdiff import diff, diff_lines, render


class TestDiff:
    def test_a_changed_item_shows_removed_then_added(self):
        result = diff(["a", "b", "c"], ["a", "d", "c"])
        assert result == [
            (" ", "a"),
            ("-", "b"),
            ("+", "d"),
            (" ", "c"),
        ]

    def test_an_insert(self):
        assert diff(["a"], ["a", "b"]) == [(" ", "a"), ("+", "b")]

    def test_a_delete(self):
        assert diff(["a", "b"], ["a"]) == [(" ", "a"), ("-", "b")]

    def test_it_diffs_any_sequence(self):
        result = diff([1, 2, 3], [1, 3])
        assert result == [(" ", 1), ("-", 2), (" ", 3)]


class TestLines:
    def test_line_diff_marks_each_line(self):
        assert render("a\nb", "a\nB") == " a\n-b\n+B"

    def test_identical_lines_are_all_context(self):
        marks = {mark for mark, _line in diff_lines("x\ny", "x\ny")}
        assert marks == {" "}


class TestMinimal:
    def test_a_shared_prefix_and_suffix_are_kept(self):
        result = diff(list("axc"), list("abc"))
        kept = [item for mark, item in result if mark == " "]
        assert kept == ["a", "c"]
