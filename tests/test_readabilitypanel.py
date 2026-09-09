from __future__ import annotations

from loom.author import Author
from loom.readabilitypanel import consensus, grades, report, spread

SAMPLE = (
    "The committee deliberated extensively. "
    "Understanding requires patience today."
)


def doc() -> Author:
    author = Author(site="alice")
    author.type_at(0, SAMPLE)
    return author


class TestGrades:
    def test_all_three_formulas_run(self):
        result = grades(doc().weave)
        assert set(result) == {"flesch-kincaid", "coleman-liau", "smog"}

    def test_the_measured_grades(self):
        result = grades(doc().weave)
        assert result["flesch-kincaid"] == 21.4
        assert result["coleman-liau"] == 26.8
        assert result["smog"] == 11.2


class TestConsensus:
    def test_the_consensus_is_the_average(self):
        assert consensus(doc().weave) == 19.8

    def test_the_spread_is_the_range(self):
        assert spread(doc().weave) == 15.6


class TestReport:
    def test_the_report_warns_about_wide_spread(self):
        assert "unusual in one" in report(doc().weave)

    def test_an_empty_document_reports_nothing(self):
        author = Author(site="alice")
        assert "no prose" in report(author.weave)
