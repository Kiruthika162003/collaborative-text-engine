from __future__ import annotations

from loom.author import Author
from loom.summarize import report, scored, summarize

TEXT = (
    "The strand is the core idea. "
    "Strand and strand and strand recur. "
    "Weather is unrelated."
)


def doc() -> Author:
    author = Author(site="alice")
    author.type_at(0, TEXT)
    return author


class TestScore:
    def test_a_keyword_dense_sentence_scores_highest(self):
        ranked = {
            s.text: score for s, score in scored(doc().weave)
        }
        dense = "Strand and strand and strand recur."
        assert ranked[dense] == max(ranked.values())

    def test_an_unrelated_sentence_scores_low(self):
        ranked = {
            s.text: score for s, score in scored(doc().weave)
        }
        assert ranked["Weather is unrelated."] < ranked[
            "The strand is the core idea."
        ]


class TestSummarize:
    def test_the_top_sentence_is_the_densest(self):
        assert summarize(doc().weave, count=1) == [
            "Strand and strand and strand recur."
        ]

    def test_the_summary_keeps_reading_order(self):
        assert summarize(doc().weave, count=2) == [
            "The strand is the core idea.",
            "Strand and strand and strand recur.",
        ]

    def test_a_count_larger_than_the_document_returns_all(self):
        assert len(summarize(doc().weave, count=99)) == 3

    def test_a_one_sentence_document_summarizes_to_itself(self):
        author = Author(site="alice")
        author.type_at(0, "Only one here.")
        assert summarize(author.weave) == ["Only one here."]


class TestReport:
    def test_the_report_disavows_insight(self):
        assert "not composition" in report(doc().weave)

    def test_an_empty_document_summarizes_to_nothing(self):
        author = Author(site="alice")
        assert "no sentences" in report(author.weave)
