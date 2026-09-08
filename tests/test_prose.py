from __future__ import annotations

from loom.author import Author
from loom.prose import (
    average_word_length,
    longest_word,
    page,
    word_count,
)


def drafted() -> Author:
    author = Author(site="alice")
    author.type_at(
        0, "the loom weaves\nconvergent cloth"
    )
    return author


class TestTheNumbers:
    def test_words_are_runs_of_ink(self):
        author = drafted()
        assert word_count(author.weave) == 5

    def test_the_longest_word_is_named(self):
        author = drafted()
        assert longest_word(author.weave) == (
            "convergent"
        )

    def test_erasure_recounts_the_living_page(self):
        author = drafted()
        author.erase_at(3, 5)
        assert word_count(author.weave) == 4

    def test_the_average_keeps_one_decimal(self):
        author = Author(site="alice")
        author.type_at(0, "ab abcd")
        assert (
            average_word_length(author.weave) == 3.0
        )


class TestThePage:
    def test_the_writers_questions_in_order(self):
        author = drafted()
        report = page(author.weave)
        assert (
            "5 word(s) on 2 line(s), 32 glyph(s)"
        ) in report
        assert (
            "longest word 'convergent' at 10"
        ) in report
        assert "average word length 5.6" in report
        assert "opinion wearing a lab coat" in report

    def test_the_empty_page_has_no_ceremony(self):
        author = Author(site="alice")
        assert page(author.weave).startswith("0 words")
