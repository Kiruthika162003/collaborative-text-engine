from __future__ import annotations

from loom.author import Author
from loom.mdlint import clean, lint, report


def codes(author: Author) -> set[str]:
    return {finding.code for finding in lint(author)}


class TestRules:
    def test_a_clean_document_passes(self):
        author = Author(site="alice")
        author.type_at(0, "# Title\n\nbody text\n")
        assert clean(author)

    def test_trailing_whitespace_is_caught(self):
        author = Author(site="alice")
        author.type_at(0, "a \nb")
        assert "MD-TRAIL" in codes(author)

    def test_a_hard_tab_is_caught(self):
        author = Author(site="alice")
        author.type_at(0, "a\tb")
        assert "MD-TAB" in codes(author)

    def test_mixed_bullets_are_caught(self):
        author = Author(site="alice")
        author.type_at(0, "* a\n- b")
        assert "MD-BULLET" in codes(author)

    def test_a_heading_level_skip_is_caught(self):
        author = Author(site="alice")
        author.type_at(0, "# A\n### C")
        assert "MD-GAP" in codes(author)

    def test_a_wrong_list_number_is_caught(self):
        author = Author(site="alice")
        author.type_at(0, "1. a\n1. b")
        assert "MD-NUM" in codes(author)

    def test_consecutive_blanks_are_caught(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\n\nb")
        assert "MD-BLANK" in codes(author)


class TestReport:
    def test_a_clean_report_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "plain text")
        assert "markdown clean" in report(author)

    def test_findings_are_ordered_by_line(self):
        author = Author(site="alice")
        author.type_at(0, "a \nb\tc")
        page = report(author)
        assert "not a full linter" in page

    def test_a_flawed_document_is_not_clean(self):
        author = Author(site="alice")
        author.type_at(0, "trailing space \n")
        assert not clean(author)
