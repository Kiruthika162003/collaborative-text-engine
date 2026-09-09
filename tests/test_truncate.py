from __future__ import annotations

import pytest

from loom.columns import display_width
from loom.errors import Invalid
from loom.truncate import middle_truncate, truncate, truncate_width


class TestTruncate:
    def test_short_text_is_returned_whole(self):
        assert truncate("hello", 20) == "hello"

    def test_the_cut_lands_on_a_word_boundary(self):
        assert truncate("the quick brown fox", 12) == "the quick..."

    def test_a_single_long_word_is_hard_cut(self):
        assert truncate("supercalifragilistic", 10) == "superca..."

    def test_the_ellipsis_counts_against_the_budget(self):
        assert len(truncate("the quick brown fox", 12)) <= 12

    def test_a_budget_smaller_than_the_ellipsis_clips_it(self):
        assert truncate("hello world", 2) == ".."

    def test_a_negative_budget_is_refused(self):
        with pytest.raises(Invalid):
            truncate("x", -1)


class TestWidth:
    def test_width_counts_wide_glyphs_as_two(self):
        text = "中文字符很长"
        out = truncate_width(text, 5)
        assert display_width(out) <= 5

    def test_latin_width_matches_length(self):
        assert truncate_width("the quick brown", 12) == "the quick..."


class TestMiddle:
    def test_the_middle_is_dropped(self):
        assert middle_truncate("abcdefghij", 7) == "ab...ij"

    def test_short_text_is_untouched(self):
        assert middle_truncate("short", 20) == "short"

    def test_the_ends_carry_the_identity(self):
        out = middle_truncate("report-2024-final.txt", 12)
        assert out.startswith("repo")
        assert out.endswith(".txt")
