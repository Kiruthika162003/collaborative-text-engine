from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid
from loom.quill import (
    ARROW_LEFT,
    ARROW_RIGHT,
    KEY_BACKSPACE,
    KEY_DELETE,
    KEY_END,
    KEY_HOME,
    Quill,
)


def fresh_quill() -> Quill:
    return Quill(author=Author(site="alice"))


class TestTyping:
    def test_keys_land_at_the_caret(self):
        quill = fresh_quill()
        quill.type_words("hello")
        assert quill.author.text() == "hello"
        assert quill.caret == 5

    def test_motions_mint_nothing(self):
        quill = fresh_quill()
        quill.type_words("ab")
        assert quill.press(ARROW_LEFT) == []
        quill.type_words("X")
        assert quill.author.text() == "aXb"

    def test_home_and_end_jump_the_line(self):
        quill = fresh_quill()
        quill.type_words("abc")
        quill.press(KEY_HOME)
        quill.type_words(">")
        quill.press(KEY_END)
        quill.type_words("<")
        assert quill.author.text() == ">abc<"

    def test_only_glyphs_and_named_keys(self):
        quill = fresh_quill()
        with pytest.raises(Invalid):
            quill.press("<paste>")


class TestEating:
    def test_backspace_eats_leftward(self):
        quill = fresh_quill()
        quill.type_words("abc")
        quill.press(KEY_BACKSPACE)
        assert quill.author.text() == "ab"
        assert quill.caret == 2

    def test_delete_eats_under_the_caret(self):
        quill = fresh_quill()
        quill.type_words("abc")
        quill.press(KEY_HOME)
        quill.press(KEY_DELETE)
        assert quill.author.text() == "bc"
        assert quill.caret == 0

    def test_the_edges_swallow_politely(self):
        quill = fresh_quill()
        assert quill.press(KEY_BACKSPACE) == []
        quill.type_words("a")
        assert quill.press(KEY_DELETE) == []
        assert "2 keystroke(s) swallowed" in (
            quill.where()
        )

    def test_arrow_right_stops_at_the_end(self):
        quill = fresh_quill()
        quill.type_words("ab")
        quill.press(ARROW_RIGHT)
        assert quill.caret == 2


class TestTheWire:
    def test_every_keystroke_returns_its_operations(
        self,
    ):
        quill = fresh_quill()
        ops = quill.press_many(
            ["h", "i", KEY_BACKSPACE, "o"]
        )
        assert len(ops) == 4
        assert quill.author.text() == "ho"

    def test_two_quills_one_author_two_carets(self):
        author = Author(site="alice")
        left = Quill(author=author)
        right = Quill(author=author)
        left.type_words("shared")
        right.caret = 6
        right.type_words("!")
        left.press(KEY_HOME)
        left.type_words(">")
        assert author.text() == ">shared!"
