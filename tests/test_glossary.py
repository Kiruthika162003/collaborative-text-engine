from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid
from loom.glossary import Glossary


def loaded() -> Glossary:
    glossary = Glossary()
    glossary.define("strand", "one glyph and its identity")
    glossary.define("version vector", "a contiguous-prefix clock")
    return glossary


class TestDefine:
    def test_a_term_is_defined_and_looked_up(self):
        glossary = loaded()
        assert glossary.lookup("Strand") == "one glyph and its identity"

    def test_lookup_is_case_insensitive(self):
        glossary = loaded()
        assert glossary.lookup("STRAND") is not None

    def test_a_blank_term_is_refused(self):
        with pytest.raises(Invalid):
            Glossary().define("  ", "something")

    def test_an_empty_definition_is_refused(self):
        with pytest.raises(Invalid):
            Glossary().define("term", "   ")


class TestFirstUse:
    def test_the_first_occurrence_is_found(self):
        author = Author(site="alice")
        author.type_at(0, "a strand and another strand")
        uses = loaded().first_uses(author.weave)
        strand_use = next(u for u in uses if u.term == "strand")
        assert strand_use.position == 2

    def test_matching_is_case_insensitive(self):
        author = Author(site="alice")
        author.type_at(0, "The Strand holds")
        uses = loaded().first_uses(author.weave)
        assert any(u.term == "strand" for u in uses)

    def test_a_term_inside_a_word_is_not_a_use(self):
        author = Author(site="alice")
        author.type_at(0, "stranded on an island")
        uses = loaded().first_uses(author.weave)
        assert not any(u.term == "strand" for u in uses)

    def test_a_multi_word_term_is_matched_whole(self):
        author = Author(site="alice")
        author.type_at(0, "the version vector clock")
        uses = loaded().first_uses(author.weave)
        assert any(u.term == "version vector" for u in uses)

    def test_a_plural_is_not_matched_a_named_limit(self):
        # the term strand is not found in strands; the match
        # does not know inflections, kept honest rather than
        # guessing plurals into false links
        author = Author(site="alice")
        author.type_at(0, "many strands here")
        uses = loaded().first_uses(author.weave)
        assert not any(u.term == "strand" for u in uses)


class TestPinAndReport:
    def test_a_first_use_pins_to_the_term_start(self):
        author = Author(site="alice")
        author.type_at(0, "a strand")
        pin = loaded().first_uses(author.weave)[0].pin
        author.type_at(0, "PRE ")
        moved = loaded().first_uses(author.weave)[0]
        assert moved.pin == pin

    def test_unused_terms_are_listed(self):
        author = Author(site="alice")
        author.type_at(0, "only strand here")
        assert loaded().unused(author.weave) == ["version vector"]

    def test_the_report_counts_used_terms(self):
        author = Author(site="alice")
        author.type_at(0, "a strand appears")
        page = loaded().report(author.weave)
        assert "2 term(s), 1 used" in page
