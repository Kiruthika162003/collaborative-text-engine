from __future__ import annotations

from loom.author import Author
from loom.paragraphstats import (
    long_paragraphs,
    para_stats,
    report,
    runaway_sentences,
)


def two_paragraphs() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "One sentence here. Two here.\n\n"
        "Another paragraph with more words in it.",
    )
    return author


class TestStats:
    def test_each_paragraph_is_measured(self):
        stats = para_stats(two_paragraphs().weave)
        assert len(stats) == 2
        assert stats[0].words == 5
        assert stats[0].sentences == 2

    def test_the_longest_sentence_is_counted(self):
        stats = para_stats(two_paragraphs().weave)
        assert stats[1].longest_sentence == 7

    def test_an_empty_document_has_no_stats(self):
        author = Author(site="alice")
        assert para_stats(author.weave) == []


class TestFlags:
    def test_a_long_paragraph_is_flagged(self):
        author = Author(site="alice")
        author.type_at(0, "word " * 130)
        assert long_paragraphs(author.weave) == [0]

    def test_a_short_paragraph_is_not_flagged(self):
        assert long_paragraphs(two_paragraphs().weave) == []

    def test_a_runaway_sentence_is_flagged(self):
        author = Author(site="alice")
        author.type_at(0, "word " * 40 + ".")
        assert runaway_sentences(author.weave) == [0]


class TestReport:
    def test_the_report_disavows_verdicts(self):
        page = report(two_paragraphs().weave)
        assert "not verdicts" in page

    def test_the_report_counts_paragraphs(self):
        page = report(two_paragraphs().weave)
        assert "2 paragraph(s)" in page

    def test_an_empty_document_reports_nothing(self):
        author = Author(site="alice")
        assert "no paragraphs" in report(author.weave)
