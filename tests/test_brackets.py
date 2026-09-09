from __future__ import annotations

from loom.brackets import (
    balance,
    depth_at,
    is_balanced,
    match_at,
    report,
)


class TestBalance:
    def test_well_nested_brackets_balance(self):
        assert is_balanced("a(b[c]{d})e")

    def test_an_unclosed_opener_is_pointed_at(self):
        found = balance("a(b[c]")
        assert not found.balanced
        assert found.unmatched_open == 1

    def test_a_stray_closer_is_pointed_at(self):
        found = balance("a)b")
        assert found.unmatched_close == 1

    def test_a_type_mismatch_is_flagged(self):
        found = balance("(]")
        assert not found.balanced


class TestMatch:
    def test_an_opener_finds_its_closer(self):
        assert match_at("a(bc)d", 1) == 4

    def test_a_closer_finds_its_opener(self):
        assert match_at("a(bc)d", 4) == 1

    def test_nested_brackets_match_correctly(self):
        assert match_at("(a(b)c)", 0) == 6
        assert match_at("(a(b)c)", 2) == 4

    def test_a_non_bracket_has_no_partner(self):
        assert match_at("abc", 1) is None

    def test_a_tangled_bracket_returns_nothing(self):
        assert match_at("(]", 0) is None


class TestDepth:
    def test_depth_counts_open_nesting(self):
        assert depth_at("((x))", 2) == 2

    def test_depth_outside_any_bracket_is_zero(self):
        assert depth_at("abc", 2) == 0


class TestReport:
    def test_a_balanced_document_says_so(self):
        assert report("(ok)") == "brackets balanced"

    def test_the_report_names_both_troubles(self):
        page = report(")a(")
        assert "stray closer at 0" in page
        assert "unclosed opener at 2" in page
