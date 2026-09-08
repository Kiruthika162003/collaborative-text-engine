from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Missing
from loom.ids import OpId
from loom.sentences import (
    render,
    sentence_count,
    sentence_of,
    sentences,
)


class TestSplitting:
    def test_terminal_punctuation_ends_a_sentence(self):
        author = Author(site="alice")
        author.type_at(0, "One here. Two there! Three?")
        found = sentences(author.weave)
        assert [s.text for s in found] == [
            "One here.",
            "Two there!",
            "Three?",
        ]

    def test_a_newline_inside_a_sentence_is_not_a_break(self):
        author = Author(site="alice")
        author.type_at(0, "a wrapped\nsentence here.")
        assert sentence_count(author.weave) == 1

    def test_abbreviations_are_over_split(self):
        # Mr. Smith reads as two sentences; telling an
        # abbreviation's dot from a full stop needs a list
        # this module does not carry, a named failure
        author = Author(site="alice")
        author.type_at(0, "Mr. Smith left.")
        assert sentence_count(author.weave) == 2

    def test_a_run_of_dots_ends_one_sentence(self):
        author = Author(site="alice")
        author.type_at(0, "wait... really")
        found = sentences(author.weave)
        assert found[0].text == "wait..."

    def test_an_unterminated_tail_is_still_a_sentence(self):
        author = Author(site="alice")
        author.type_at(0, "closed. open tail")
        found = sentences(author.weave)
        assert [s.text for s in found] == ["closed.", "open tail"]


class TestPin:
    def test_a_sentence_pins_to_its_first_glyph(self):
        author = Author(site="alice")
        author.type_at(0, "first. second.")
        pin = sentences(author.weave)[1].pin
        author.type_at(0, "PRE ")
        moved = sentences(author.weave)
        found = next(s for s in moved if s.pin == pin)
        assert found.text == "second."

    def test_the_sentence_of_a_strand_is_found(self):
        author = Author(site="alice")
        ops = author.type_at(0, "aaa. bbb. ccc.")
        # a glyph in the second sentence (index 5 = first b)
        assert sentence_of(author.weave, ops[5].id) == 1

    def test_a_missing_strand_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "x.")
        with pytest.raises(Missing):
            sentence_of(author.weave, OpId("ghost", 9))


class TestRender:
    def test_render_lists_each_sentence(self):
        author = Author(site="alice")
        author.type_at(0, "One. Two.")
        page = render(author.weave)
        assert "2 sentence(s)" in page

    def test_an_empty_document_has_no_sentences(self):
        author = Author(site="alice")
        assert "no sentences" in render(author.weave)
