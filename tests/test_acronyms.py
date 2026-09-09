from __future__ import annotations

from loom.acronyms import acronyms, definitions, report, undefined
from loom.author import Author


def technical() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "The API (Application Programming Interface) speaks HTTP. "
        "HyperText Transfer Protocol (HTTP) is old. We ship JSON.",
    )
    return author


class TestDetect:
    def test_all_caps_tokens_are_acronyms(self):
        tokens = {a.token for a in acronyms(technical().weave)}
        assert {"API", "HTTP", "JSON"} <= tokens

    def test_single_capitals_are_not_acronyms(self):
        author = Author(site="alice")
        author.type_at(0, "I saw A cat")
        assert acronyms(author.weave) == []

    def test_the_first_position_is_recorded(self):
        author = Author(site="alice")
        author.type_at(0, "say API then API again")
        first = next(a for a in acronyms(author.weave) if a.token == "API")
        assert first.position == 4


class TestDefinitions:
    def test_acronym_then_expansion_is_caught(self):
        assert definitions(technical().weave)["API"] == (
            "Application Programming Interface"
        )

    def test_expansion_then_acronym_is_caught(self):
        assert definitions(technical().weave)["HTTP"] == (
            "HyperText Transfer Protocol"
        )


class TestUndefined:
    def test_an_undefined_acronym_is_flagged(self):
        assert undefined(technical().weave) == ["JSON"]

    def test_a_fully_defined_document_flags_none(self):
        author = Author(site="alice")
        author.type_at(0, "The CPU (Central Processing Unit) runs.")
        assert undefined(author.weave) == []


class TestReport:
    def test_the_report_counts_and_lists_undefined(self):
        page = report(technical().weave)
        assert "3 acronym(s), 2 defined" in page
        assert "undefined: JSON" in page

    def test_a_plain_document_reports_no_acronyms(self):
        author = Author(site="alice")
        author.type_at(0, "just lower case words")
        assert "spells everything out" in report(author.weave)
