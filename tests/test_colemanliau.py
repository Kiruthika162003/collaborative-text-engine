from __future__ import annotations

from loom.author import Author
from loom.colemanliau import index, report


class TestIndex:
    def test_the_simple_sample_measures_low(self):
        author = Author(site="alice")
        author.type_at(0, "The cat sat on the mat. The dog ran far.")
        assert index(author.weave) == -4.7

    def test_long_words_raise_the_grade(self):
        author = Author(site="alice")
        author.type_at(
            0,
            "Extraordinarily complicated sesquipedalian "
            "terminology obfuscates comprehension.",
        )
        assert index(author.weave) == 51.8

    def test_an_empty_document_scores_zero(self):
        author = Author(site="alice")
        assert index(author.weave) == 0.0


class TestReport:
    def test_the_report_names_the_tradeoff(self):
        author = Author(site="alice")
        author.type_at(0, "Some prose to grade here today.")
        assert "no syllables" in report(author.weave)

    def test_an_empty_document_reports_nothing(self):
        author = Author(site="alice")
        assert "no prose" in report(author.weave)
