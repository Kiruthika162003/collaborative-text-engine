from __future__ import annotations

from loom.commas import parse, render


class TestParse:
    def test_simple_rows_parse(self):
        assert parse("a,b\nc,d") == [["a", "b"], ["c", "d"]]

    def test_a_quoted_field_holds_a_comma(self):
        assert parse('a,"b,c",d') == [["a", "b,c", "d"]]

    def test_a_quoted_field_holds_a_newline(self):
        assert parse('"line one\nline two",x') == [["line one\nline two", "x"]]

    def test_a_doubled_quote_is_one_quote(self):
        assert parse('"she said ""hi"""') == [['she said "hi"']]

    def test_a_trailing_newline_makes_no_phantom_row(self):
        assert parse("a,b\n") == [["a", "b"]]

    def test_an_empty_field_is_kept(self):
        assert parse("a,,c") == [["a", "", "c"]]


class TestRender:
    def test_plain_fields_stay_bare(self):
        assert render([["a", "b"]]) == "a,b"

    def test_a_comma_field_is_quoted(self):
        assert render([["a,b", "c"]]) == '"a,b",c'

    def test_an_interior_quote_is_doubled(self):
        assert render([['say "hi"']]) == '"say ""hi"""'


class TestRoundTrip:
    def test_render_then_parse_is_identity(self):
        rows = [["a", "b,c"], ['d"e', "f\ng"], ["", "h"]]
        assert parse(render(rows)) == rows


class TestTypes:
    def test_a_leading_zero_survives_as_a_string(self):
        assert parse("007,name") == [["007", "name"]]
