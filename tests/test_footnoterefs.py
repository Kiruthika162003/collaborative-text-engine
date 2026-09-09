from __future__ import annotations

from loom.footnoterefs import (
    definitions,
    numbering,
    references,
    report,
    undefined,
    unused,
)

DOC = "See this[^note] and that[^two].\n\n[^note]: first\n[^two]: second"


class TestParse:
    def test_references_are_read_in_order(self):
        assert references(DOC) == ["note", "two"]

    def test_definitions_are_read(self):
        assert definitions(DOC) == {"note": "first", "two": "second"}

    def test_a_definition_label_is_not_a_reference(self):
        assert references("[^x]: only a definition") == []


class TestNumbering:
    def test_numbering_follows_first_reference(self):
        assert numbering(DOC) == {"note": 1, "two": 2}

    def test_a_repeated_reference_keeps_its_number(self):
        text = "a[^x] b[^y] c[^x]"
        assert numbering(text) == {"x": 1, "y": 2}


class TestResolution:
    def test_an_undefined_reference_is_flagged(self):
        assert undefined("see[^ghost] here") == ["ghost"]

    def test_an_unused_definition_is_flagged(self):
        assert unused("[^x]: never referenced") == ["x"]

    def test_a_resolved_document_is_clean(self):
        assert undefined(DOC) == []
        assert unused(DOC) == []


class TestReport:
    def test_the_report_counts(self):
        assert "2 footnote(s), 2 definition(s)" in report(DOC)

    def test_a_plain_document_has_nothing(self):
        assert "nothing to resolve" in report("just prose")
