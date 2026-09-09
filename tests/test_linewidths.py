from __future__ import annotations

from loom.author import Author
from loom.linewidths import longest_line, over_limit, report, widths


class TestWidths:
    def test_widths_are_measured_per_line(self):
        author = Author(site="alice")
        author.type_at(0, "short\nthis line is quite long here")
        assert widths(author.weave) == [5, 28]

    def test_wide_glyphs_count_double(self):
        author = Author(site="alice")
        author.type_at(0, "中文")
        assert widths(author.weave) == [4]


class TestOverLimit:
    def test_lines_over_the_limit_are_listed(self):
        author = Author(site="alice")
        author.type_at(0, "short\nthis line is quite long here")
        assert over_limit(author.weave, 10) == [(1, 28)]

    def test_a_document_within_the_limit_lists_none(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb\nc")
        assert over_limit(author.weave, 80) == []


class TestLongest:
    def test_the_longest_line_is_named(self):
        author = Author(site="alice")
        author.type_at(0, "a\nlonger line")
        assert longest_line(author.weave) == (1, 11)


class TestReport:
    def test_the_report_lists_over_limit_lines(self):
        author = Author(site="alice")
        author.type_at(0, "tiny\nthis one is definitely too wide for eight")
        page = report(author.weave, 8)
        assert "line 1:" in page

    def test_a_fitting_document_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "fits")
        assert "every line fits" in report(author.weave, 80)
