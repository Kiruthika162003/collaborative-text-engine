from __future__ import annotations

from loom.author import Author
from loom.concordance import (
    distinct,
    frequencies,
    positions,
    report,
    richness,
    top,
)


def prose() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "the fox and the hound and the fox again",
    )
    return author


class TestCounting:
    def test_words_are_vocabulary_not_typography(self):
        author = Author(site="alice")
        author.type_at(0, "Quick, quick! QUICK.")
        assert frequencies(author.weave)["quick"] == 3

    def test_distinct_counts_the_vocabulary(self):
        author = prose()
        assert distinct(author.weave) == 5

    def test_the_leaned_on_word_rises_to_the_top(self):
        author = prose()
        assert top(author.weave, 1) == [("the", 3)]


class TestPositionsAndRichness:
    def test_positions_find_each_occurrence(self):
        author = prose()
        assert positions(author.weave, "fox") == [4, 30]

    def test_richness_rises_with_variety(self):
        varied = Author(site="alice")
        varied.type_at(0, "one two three four")
        repeated = Author(site="alice")
        repeated.type_at(0, "one one one one")
        assert richness(varied.weave) > richness(
            repeated.weave
        )

    def test_positions_track_the_living_cloth(self):
        author = prose()
        author.type_at(0, ">>> ")
        assert positions(author.weave, "fox") == [8, 34]


class TestTheReport:
    def test_the_report_names_the_top_words(self):
        author = prose()
        page = report(author.weave)
        assert "9 word(s), 5 distinct" in page
        assert "the: 3" in page
        assert "pretending to count" in page

    def test_the_empty_page_has_no_vocabulary(self):
        author = Author(site="alice")
        assert "no vocabulary" in report(author.weave)
