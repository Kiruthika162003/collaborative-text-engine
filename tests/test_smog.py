from __future__ import annotations

from loom.author import Author
from loom.smog import grade, polysyllables, report


class TestPolysyllables:
    def test_long_words_are_counted(self):
        author = Author(site="alice")
        author.type_at(
            0,
            "The committee deliberated extensively. "
            "Understanding requires patience.",
        )
        assert polysyllables(author.weave) == 4

    def test_short_words_are_not_counted(self):
        author = Author(site="alice")
        author.type_at(0, "the cat sat on the mat")
        assert polysyllables(author.weave) == 0


class TestGrade:
    def test_the_complex_sample_grades_high(self):
        author = Author(site="alice")
        author.type_at(
            0,
            "The committee deliberated extensively. "
            "Understanding requires patience.",
        )
        assert grade(author.weave) == 11.2

    def test_a_simple_sample_grades_at_the_base(self):
        author = Author(site="alice")
        author.type_at(0, "The cat sat. The dog ran.")
        assert grade(author.weave) == 3.1

    def test_an_empty_document_scores_zero(self):
        author = Author(site="alice")
        assert grade(author.weave) == 0.0


class TestReport:
    def test_the_report_names_the_snippet_caveat(self):
        author = Author(site="alice")
        author.type_at(0, "Some understanding develops slowly here.")
        assert "noisy on a snippet" in report(author.weave)

    def test_an_empty_document_reports_no_prose(self):
        author = Author(site="alice")
        assert "needs prose" in report(author.weave)
