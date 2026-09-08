from __future__ import annotations

import pytest

from loom.author import Author
from loom.citations import Bibliography, Citation, Citations, Source
from loom.errors import Diverged, Invalid, Missing
from loom.ids import OpId

SMITH = Source(key="smith", author="Smith, J", title="On Weaving", year=2020)
JONES = Source(key="jones", author="Jones, K", title="On Merging", year=2019)


def cited() -> tuple[Author, Citations, list]:
    author = Author(site="alice")
    ops = author.type_at(0, "a b a")
    biblio = Bibliography()
    biblio.enter(SMITH)
    biblio.enter(JONES)
    marks = Citations(weave=author.weave, bibliography=biblio)
    marks.cite(Citation(OpId("bob", 1), ops[0].id, "smith"))
    marks.cite(Citation(OpId("bob", 2), ops[2].id, "jones"))
    marks.cite(Citation(OpId("bob", 3), ops[4].id, "smith"))
    return author, marks, ops


class TestSource:
    def test_a_reference_reads_as_a_citation_line(self):
        assert SMITH.reference() == "Smith, J (2020). On Weaving."

    def test_a_yearless_source_omits_the_year(self):
        source = Source(key="x", author="Doe", title="Untimed")
        assert "(" not in source.reference()

    def test_a_source_without_author_or_title_is_refused(self):
        with pytest.raises(Invalid):
            Source(key="x", author="  ", title="")


class TestBibliography:
    def test_a_repeated_entry_is_idempotent(self):
        biblio = Bibliography()
        biblio.enter(SMITH)
        biblio.enter(SMITH)
        assert len(biblio.sources) == 1

    def test_two_papers_under_one_key_diverge(self):
        biblio = Bibliography()
        biblio.enter(SMITH)
        clash = Source(key="smith", author="Other", title="Different")
        with pytest.raises(Diverged):
            biblio.enter(clash)

    def test_merging_unions_by_key(self):
        left = Bibliography()
        left.enter(SMITH)
        right = Bibliography()
        right.enter(JONES)
        merged = left.merge(right)
        assert merged.has("smith")
        assert merged.has("jones")


class TestNumbering:
    def test_distinct_sources_number_by_first_appearance(self):
        _author, marks, _ops = cited()
        numbers = marks.numbering()
        assert numbers == {"smith": 1, "jones": 2}

    def test_a_repeat_citation_reuses_its_number(self):
        _author, marks, _ops = cited()
        assert marks.in_text() == [1, 2, 1]

    def test_the_works_cited_lists_each_source_once(self):
        _author, marks, _ops = cited()
        page = marks.works_cited()
        assert page.count("On Weaving") == 1
        assert "[1] Smith, J (2020). On Weaving." in page
        assert "[2] Jones, K (2019). On Merging." in page


class TestAnchoring:
    def test_a_citation_of_an_unknown_key_is_refused(self):
        author = Author(site="alice")
        ops = author.type_at(0, "x")
        marks = Citations(weave=author.weave, bibliography=Bibliography())
        with pytest.raises(Missing):
            marks.cite(Citation(OpId("bob", 1), ops[0].id, "ghost"))

    def test_a_sheared_anchor_drops_from_the_numbering(self):
        author, marks, _ops = cited()
        author.erase_at(2, 1)
        assert marks.in_text() == [1, 1]

    def test_an_uncited_document_has_no_works_cited(self):
        author = Author(site="alice")
        author.type_at(0, "plain")
        marks = Citations(weave=author.weave, bibliography=Bibliography())
        assert marks.works_cited() == "no citations"
