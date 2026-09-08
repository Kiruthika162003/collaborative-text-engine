from __future__ import annotations

from loom.threeway import merge


class TestCleanMerges:
    def test_disjoint_edits_both_land(self):
        result = merge(
            "one\ntwo\nthree\nfour",
            "one\nTWO\nthree\nfour",
            "one\ntwo\nthree\nFOUR",
        )
        assert result.is_clean()
        assert result.text == (
            "one\nTWO\nthree\nFOUR"
        )

    def test_one_sided_edits_are_taken(self):
        result = merge(
            "a\nb\nc",
            "a\nB\nc",
            "a\nb\nc",
        )
        assert result.is_clean()
        assert result.text == "a\nB\nc"

    def test_identical_changes_collapse(self):
        result = merge(
            "a\nx\nb",
            "a\nFIX\nb",
            "a\nFIX\nb",
        )
        assert result.is_clean()
        assert result.text == "a\nFIX\nb"

    def test_untouched_base_is_kept(self):
        result = merge("keep\nme", "keep\nme", "keep\nme")
        assert result.is_clean()
        assert result.text == "keep\nme"


class TestConflicts:
    def test_same_region_changed_differently_conflicts(
        self,
    ):
        result = merge(
            "a\nx\nb",
            "a\nOURS\nb",
            "a\nTHEIRS\nb",
        )
        assert not result.is_clean()
        assert result.conflicts == 1
        assert "<<<<<<< ours" in result.text
        assert "OURS" in result.text
        assert "THEIRS" in result.text
        assert ">>>>>>> theirs" in result.text

    def test_the_merge_never_silently_picks_a_side(self):
        result = merge("v", "ours", "theirs")
        assert result.conflicts == 1

    def test_the_count_is_what_a_caller_checks(self):
        result = merge(
            "a\nb\nc\nd",
            "a\nB1\nc\nD1",
            "a\nB2\nc\nD2",
        )
        assert result.conflicts == 2
