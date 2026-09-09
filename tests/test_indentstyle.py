from __future__ import annotations

from loom.author import Author
from loom.indentstyle import detect, indent_width, is_mixed, report


class TestDetect:
    def test_space_indentation_is_detected_with_width(self):
        author = Author(site="alice")
        author.type_at(0, "def f():\n  return 1\n  x = 2")
        assert detect(author.weave) == ("spaces", 2)

    def test_tab_indentation_is_detected(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\tb")
        assert detect(author.weave) == ("tabs", 1)

    def test_mixed_indentation_is_flagged(self):
        author = Author(site="alice")
        author.type_at(0, "  a\n\tb")
        assert detect(author.weave)[0] == "mixed"
        assert is_mixed(author.weave)

    def test_a_flat_document_has_no_style(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb\nc")
        assert detect(author.weave) == ("none", 0)


class TestWidth:
    def test_the_width_is_the_smallest_positive_indent(self):
        author = Author(site="alice")
        author.type_at(0, "a\n    b\n  c")
        assert indent_width(author.weave) == 2


class TestReport:
    def test_the_report_names_spaces_and_width(self):
        author = Author(site="alice")
        author.type_at(0, "a\n  b")
        assert "width 2" in report(author.weave)

    def test_the_report_flags_mixed(self):
        author = Author(site="alice")
        author.type_at(0, "  a\n\tb")
        assert "mixed indentation" in report(author.weave)

    def test_a_flat_document_reports_flat(self):
        author = Author(site="alice")
        author.type_at(0, "flat")
        assert "flat" in report(author.weave)
