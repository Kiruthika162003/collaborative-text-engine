from __future__ import annotations

from loom.author import Author
from loom.spellcheck import check, clean, report

LEXICON = {"the", "cat", "sat", "on", "mat"}


class TestCheck:
    def test_a_misspelling_is_flagged_with_suggestions(self):
        author = Author(site="alice")
        author.type_at(0, "the kat sat")
        found = check(author.weave, LEXICON)
        assert len(found) == 1
        assert found[0].word == "kat"
        assert "cat" in found[0].suggestions

    def test_a_covered_document_is_clean(self):
        author = Author(site="alice")
        author.type_at(0, "the cat sat on the mat")
        assert clean(author.weave, LEXICON)

    def test_words_inside_a_code_fence_are_skipped(self):
        author = Author(site="alice")
        author.type_at(0, "```\nkat\n```\nthe cat")
        assert check(author.weave, LEXICON) == []

    def test_a_word_with_no_near_neighbour_has_no_suggestions(self):
        author = Author(site="alice")
        author.type_at(0, "xyzzy here")
        found = check(author.weave, LEXICON)
        misspelled = next(c for c in found if c.word == "xyzzy")
        assert misspelled.suggestions == []


class TestReport:
    def test_a_clean_report_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "the cat")
        assert "spelling clean" in report(author.weave, LEXICON)

    def test_the_report_offers_a_suggestion(self):
        author = Author(site="alice")
        author.type_at(0, "the kat")
        assert "did you mean" in report(author.weave, LEXICON)
