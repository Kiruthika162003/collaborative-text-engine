from __future__ import annotations

from loom.author import Author
from loom.proofread import clean, findings, report


class TestFindings:
    def test_a_doubled_word_is_reported(self):
        author = Author(site="alice")
        author.type_at(0, "this is is fine")
        assert any("doubled word" in item for item in findings(author.weave))

    def test_an_unbalanced_bracket_is_reported(self):
        author = Author(site="alice")
        author.type_at(0, "a (b c")
        assert "unbalanced brackets" in findings(author.weave)

    def test_a_duplicated_line_is_reported(self):
        author = Author(site="alice")
        author.type_at(0, "row\nrow\ndone")
        assert any("duplicated line" in item for item in findings(author.weave))

    def test_an_undefined_acronym_is_reported(self):
        author = Author(site="alice")
        author.type_at(0, "we love JSON here")
        assert any("undefined acronym" in item for item in findings(author.weave))


class TestClean:
    def test_a_clean_document_finds_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "a simple clean sentence")
        assert clean(author.weave)

    def test_a_flawed_document_is_not_clean(self):
        author = Author(site="alice")
        author.type_at(0, "the the end")
        assert not clean(author.weave)


class TestReport:
    def test_a_clean_report_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "nothing wrong here")
        assert "proofread clean" in report(author.weave)

    def test_a_flawed_report_disavows_correcting(self):
        author = Author(site="alice")
        author.type_at(0, "a (broken bracket")
        page = report(author.weave)
        assert "not a corrector" in page

    def test_brackets_are_ordered_first(self):
        author = Author(site="alice")
        author.type_at(0, "the the ( unbalanced")
        first = findings(author.weave)[0]
        assert first == "unbalanced brackets"
