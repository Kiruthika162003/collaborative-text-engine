from __future__ import annotations

from loom.bibstyle import alphabetical, author_year, bibliography, in_text
from loom.citations import Bibliography, Source


def loaded() -> Bibliography:
    biblio = Bibliography()
    biblio.enter(Source("smith", "Smith, J", "On Weaving", 2020))
    biblio.enter(Source("adams", "Adams, K", "On Anchors", 2019))
    return biblio


class TestAuthorYear:
    def test_the_parenthetical_is_author_and_year(self):
        source = Source("x", "Doe, J", "A Study", 2021)
        assert author_year(source) == "(Doe, J, 2021)"

    def test_a_yearless_source_cites_n_d(self):
        source = Source("x", "Doe", "Undated")
        assert author_year(source) == "(Doe, n.d.)"


class TestAlphabetical:
    def test_sources_sort_by_author(self):
        lines = alphabetical(loaded())
        assert lines[0].startswith("Adams")
        assert lines[1].startswith("Smith")

    def test_an_authorless_source_sorts_by_title(self):
        biblio = Bibliography()
        biblio.enter(Source("z", "", "Aardvarks", 2000))
        biblio.enter(Source("s", "Smith", "Zebras", 2000))
        assert alphabetical(biblio)[0].startswith("Anon")


class TestRender:
    def test_the_bibliography_renders_sorted(self):
        page = bibliography(loaded())
        assert page.splitlines()[0].startswith("Adams")

    def test_an_empty_bibliography_says_so(self):
        assert "lists nothing" in bibliography(Bibliography())

    def test_in_text_cites_a_known_key(self):
        assert in_text(loaded(), "smith") == "(Smith, J, 2020)"

    def test_in_text_flags_an_unknown_key(self):
        assert "unknown source" in in_text(loaded(), "ghost")
