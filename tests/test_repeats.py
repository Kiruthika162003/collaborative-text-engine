from __future__ import annotations

from loom.author import Author
from loom.repeats import doubled_words, duplicate_lines, report


class TestDoubledWords:
    def test_a_doubled_word_is_found(self):
        author = Author(site="alice")
        author.type_at(0, "this is is a test")
        found = doubled_words(author.weave)
        assert [r.word for r in found] == ["is"]

    def test_the_double_is_case_folded(self):
        author = Author(site="alice")
        author.type_at(0, "The the cat")
        assert len(doubled_words(author.weave)) == 1

    def test_punctuation_between_is_not_a_double(self):
        author = Author(site="alice")
        author.type_at(0, "that, that clause")
        assert doubled_words(author.weave) == []

    def test_a_double_across_a_newline_still_counts(self):
        author = Author(site="alice")
        author.type_at(0, "end word\nword start")
        assert len(doubled_words(author.weave)) == 1


class TestPin:
    def test_a_double_pins_to_the_second_word(self):
        author = Author(site="alice")
        ops = author.type_at(0, "a a b")
        pin = doubled_words(author.weave)[0].pin
        assert pin == ops[2].id


class TestDuplicateLines:
    def test_an_adjacent_duplicate_line_is_found(self):
        author = Author(site="alice")
        author.type_at(0, "keep\nsame\nsame\ndone")
        assert duplicate_lines(author.weave) == [2]

    def test_blank_lines_are_not_duplicates(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\n\nb")
        assert duplicate_lines(author.weave) == []


class TestReport:
    def test_the_report_lists_both_kinds(self):
        author = Author(site="alice")
        author.type_at(0, "the the words\nrepeat me\nrepeat me")
        page = report(author.weave)
        assert "doubled word(s): the" in page
        assert "duplicated line(s) at 2" in page

    def test_a_clean_document_reports_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "clean prose here")
        assert "nothing to look at" in report(author.weave)
