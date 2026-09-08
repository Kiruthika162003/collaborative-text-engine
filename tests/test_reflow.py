from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.reflow import (
    fits_within,
    longest_line,
    reflow,
)


class TestWrapping:
    def test_greedy_fill_breaks_before_overflow(self):
        wrapped = reflow(
            "the quick brown fox jumps over the lazy dog",
            15,
        )
        for line in wrapped.split("\n"):
            assert len(line) <= 15

    def test_a_long_word_is_never_chopped(self):
        wrapped = reflow(
            "short https://a-very-long-url-here end", 12
        )
        assert (
            "https://a-very-long-url-here"
            in wrapped.split("\n")
        )

    def test_soft_wraps_become_spaces(self):
        wrapped = reflow("one\ntwo three", 80)
        assert wrapped == "one two three"

    def test_paragraph_breaks_are_preserved(self):
        wrapped = reflow("one two\n\nthree four", 80)
        assert "\n\n" in wrapped

    def test_a_zero_width_is_refused(self):
        with pytest.raises(Invalid):
            reflow("text", 0)


class TestMeasures:
    def test_longest_line_is_reported(self):
        assert (
            longest_line("aa\nbbbb\nc") == 4
        )

    def test_fits_within_tolerates_lone_long_words(
        self,
    ):
        wrapped = reflow(
            "short https://a-very-long-url-here end", 12
        )
        assert fits_within(wrapped, 12)

    def test_fits_within_catches_a_wide_line(self):
        assert not fits_within(
            "two words here", 5
        )
