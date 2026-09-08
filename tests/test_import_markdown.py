from __future__ import annotations

from loom.export_markdown import to_markdown
from loom.import_markdown import load, parse


class TestParsing:
    def test_stars_become_spans_over_clean_text(self):
        parsed = parse("plain **bold** and *italic* end")
        assert parsed.text == (
            "plain bold and italic end"
        )
        assert ("bold", 6, 10) in parsed.spans
        assert ("italic", 15, 21) in parsed.spans

    def test_a_lone_star_stays_literal(self):
        parsed = parse("2 * 3 = 6")
        assert parsed.text == "2 * 3 = 6"
        assert parsed.spans == []

    def test_unmatched_bold_is_literal(self):
        parsed = parse("**unclosed here")
        assert parsed.text == "**unclosed here"
        assert parsed.spans == []


class TestLoading:
    def test_an_imported_doc_looks_typed_in(self):
        author, wardrobe = load(
            "plain **bold** and *italic* end"
        )
        assert author.text() == (
            "plain bold and italic end"
        )
        spans = dict(wardrobe.spans())
        assert spans["bold"] == frozenset({"bold"})
        assert spans["italic"] == frozenset({"italic"})

    def test_import_export_round_trips(self):
        source = "plain **bold** and *italic* end"
        _author, wardrobe = load(source)
        assert to_markdown(wardrobe) == source

    def test_the_importer_names_the_strands(self):
        author, _wardrobe = load(
            "hello", importer="import"
        )
        assert all(
            strand.id.site == "import"
            for strand in author.weave.strands
        )

    def test_empty_source_imports_cleanly(self):
        author, wardrobe = load("")
        assert author.text() == ""
        assert wardrobe.spans() == []
