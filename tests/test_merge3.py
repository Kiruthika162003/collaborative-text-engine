from __future__ import annotations

from loom.author import Author
from loom.conflictmarkers import resolve
from loom.merge3 import conflicts, merge3


class TestShortCircuits:
    def test_only_theirs_changed_takes_theirs(self):
        assert merge3("a\nb\nc", "a\nb\nc", "a\nB\nc") == ("a\nB\nc", False)

    def test_only_ours_changed_takes_ours(self):
        assert merge3("a\nb\nc", "A\nb\nc", "a\nb\nc") == ("A\nb\nc", False)

    def test_identical_edits_take_one(self):
        assert merge3("a\nb", "a\nZ", "a\nZ") == ("a\nZ", False)


class TestMerge:
    def test_non_overlapping_edits_combine(self):
        merged, conflict = merge3("a\nb\nc", "A\nb\nc", "a\nb\nC")
        assert merged == "A\nb\nC"
        assert not conflict

    def test_overlapping_edits_conflict(self):
        merged, conflict = merge3("a\nb\nc", "a\nX\nc", "a\nY\nc")
        assert conflict
        assert "<<<<<<< ours" in merged
        assert "X" in merged and "Y" in merged

    def test_conflicts_predicate(self):
        assert conflicts("a\nb", "a\nX", "a\nY")
        assert not conflicts("a\nb", "a\nb", "a\nX")


class TestIntegration:
    def test_a_conflict_can_be_resolved_by_the_marker_tool(self):
        merged, _conflict = merge3("a\nb\nc", "a\nX\nc", "a\nY\nc")
        author = Author(site="alice")
        author.type_at(0, merged)
        resolve(author, 0, "ours")
        assert author.text() == "a\nX\nc"
