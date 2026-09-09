from __future__ import annotations

import pytest

from loom.author import Author
from loom.diversity import report, type_token_ratio, windowed_ttr


class TestRatio:
    def test_a_repeated_word_lowers_the_ratio(self):
        author = Author(site="alice")
        author.type_at(0, "a b c a")
        assert type_token_ratio(author.weave) == 0.75

    def test_all_distinct_scores_one(self):
        author = Author(site="alice")
        author.type_at(0, "one two three")
        assert type_token_ratio(author.weave) == 1.0

    def test_one_word_repeated_scores_low(self):
        author = Author(site="alice")
        author.type_at(0, "x x x x")
        assert type_token_ratio(author.weave) == 0.25

    def test_case_is_folded(self):
        author = Author(site="alice")
        author.type_at(0, "The the THE")
        assert type_token_ratio(author.weave) == pytest.approx(1 / 3)

    def test_an_empty_document_scores_zero(self):
        author = Author(site="alice")
        assert type_token_ratio(author.weave) == 0.0


class TestWindowed:
    def test_a_short_text_uses_the_raw_ratio(self):
        author = Author(site="alice")
        author.type_at(0, "a b c")
        assert windowed_ttr(author.weave, window=100) == 1.0

    def test_windows_average_the_ratio(self):
        author = Author(site="alice")
        author.type_at(0, "a b a b " * 25)
        assert windowed_ttr(author.weave, window=4) == pytest.approx(0.5)


class TestReport:
    def test_the_report_disavows_quality(self):
        author = Author(site="alice")
        author.type_at(0, "some words here now")
        assert "not a quality score" in report(author.weave)

    def test_an_empty_document_reports_nothing(self):
        author = Author(site="alice")
        assert "nothing to measure" in report(author.weave)
