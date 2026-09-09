from __future__ import annotations

from loom.bibtex import into_bibliography, parse

BRACED = "@article{smith2020, author={Smith, J}, title={On Weaving}, year={2020}}"
QUOTED = '@book{jones19, author="Jones, K", title="On Merging", year="2019"}'


class TestParse:
    def test_a_braced_entry_parses(self):
        source = parse(BRACED)[0]
        assert source.key == "smith2020"
        assert source.author == "Smith, J"
        assert source.title == "On Weaving"
        assert source.year == 2020

    def test_a_quoted_entry_parses(self):
        source = parse(QUOTED)[0]
        assert source.author == "Jones, K"
        assert source.year == 2019

    def test_two_entries_both_parse(self):
        assert len(parse(BRACED + "\n" + QUOTED)) == 2

    def test_a_non_numeric_year_becomes_none(self):
        source = parse("@misc{x, title={Draft}, year={in press}}")[0]
        assert source.year is None

    def test_empty_text_parses_to_nothing(self):
        assert parse("") == []


class TestBibliography:
    def test_entries_load_into_a_bibliography(self):
        biblio = into_bibliography(BRACED + "\n" + QUOTED)
        assert biblio.has("smith2020")
        assert biblio.has("jones19")
