from __future__ import annotations

from loom.author import Author
from loom.keywords import frequencies, keywords, report, top_terms


def about_weaving() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "The strand names a strand and every strand is a strand "
        "of the weave.",
    )
    return author


class TestFrequencies:
    def test_function_words_are_dropped(self):
        counts = frequencies(about_weaving().weave)
        assert "the" not in counts
        assert "and" not in counts

    def test_content_words_are_counted(self):
        counts = frequencies(about_weaving().weave)
        assert counts["strand"] == 4
        assert counts["weave"] == 1

    def test_case_is_folded(self):
        author = Author(site="alice")
        author.type_at(0, "Loom loom LOOM")
        assert frequencies(author.weave)["loom"] == 3

    def test_single_letters_are_dropped(self):
        author = Author(site="alice")
        author.type_at(0, "a b c weave")
        assert list(frequencies(author.weave)) == ["weave"]


class TestKeywords:
    def test_the_most_frequent_content_word_leads(self):
        assert top_terms(about_weaving().weave)[0] == "strand"

    def test_a_limit_caps_the_list(self):
        author = Author(site="alice")
        author.type_at(0, "cat dog fish bird frog newt toad")
        assert len(keywords(author.weave, limit=3)) == 3

    def test_ties_break_alphabetically(self):
        author = Author(site="alice")
        author.type_at(0, "zebra apple")
        assert top_terms(author.weave) == ["apple", "zebra"]


class TestReport:
    def test_the_report_disavows_importance(self):
        page = report(about_weaving().weave)
        assert "not a claim about" in page

    def test_a_function_only_document_has_no_keywords(self):
        author = Author(site="alice")
        author.type_at(0, "the and of to is")
        assert "all function words" in report(author.weave)
