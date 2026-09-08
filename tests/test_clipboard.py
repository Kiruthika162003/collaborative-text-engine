from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.clipboard import Clipboard
from loom.errors import Invalid


def loaded() -> tuple[Author, Clipboard]:
    author = Author(site="alice")
    author.type_at(0, "the quick brown fox")
    return author, Clipboard()


class TestCopy:
    def test_copy_takes_text_without_shearing(self):
        author, board = loaded()
        board.copy(author, 4, 5)
        assert board.held == "quick"
        assert author.text() == "the quick brown fox"

    def test_an_empty_clipboard_has_no_content(self):
        assert not Clipboard().has_content()


class TestCut:
    def test_cut_takes_and_shears(self):
        author, board = loaded()
        board.cut(author, 4, 6)
        assert board.held == "quick "
        assert author.text() == "the brown fox"

    def test_pasting_cut_text_elsewhere(self):
        author, board = loaded()
        board.cut(author, 4, 6)
        board.paste(author, author.weave.visible_count())
        assert author.text() == "the brown foxquick "


class TestPaste:
    def test_paste_mints_new_strands(self):
        author, board = loaded()
        board.copy(author, 4, 5)
        pasted = board.paste(author, 0)
        original = author.weave.strand_at_visible(9)
        assert pasted[0].id != original.id

    def test_pasting_an_empty_clipboard_is_refused(self):
        author, _board = loaded()
        with pytest.raises(Invalid):
            Clipboard().paste(author, 0)


class TestAcrossDocuments:
    def test_a_cut_pastes_as_ordinary_typing(self):
        board = Clipboard()
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "keep move"),
        )
        circle.settle()
        cut_ops = board.cut(circle.author("alice"), 4, 5)
        paste_ops = board.paste(
            circle.author("alice"), 0
        )
        circle.say("alice", cut_ops + paste_ops)
        circle.settle()
        assert circle.converged() == circle.author(
            "bob"
        ).text()
        assert "move" in circle.converged()
