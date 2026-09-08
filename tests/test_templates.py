from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid, Missing
from loom.templates import TemplateBook


def stocked() -> TemplateBook:
    book = TemplateBook()
    book.define("sig", "Best,\nKiruthika")
    book.define("greet", "Dear {name}, {closing}")
    return book


class TestDefining:
    def test_snippets_report_their_holes(self):
        book = stocked()
        assert book.holes("greet") == [
            "name",
            "closing",
        ]
        assert book.holes("sig") == []

    def test_an_empty_snippet_is_refused(self):
        with pytest.raises(Invalid):
            TemplateBook().define("bad", "")

    def test_the_roster_counts_holes(self):
        page = stocked().roster()
        assert "sig" in page
        assert "greet (2 hole(s))" in page


class TestExpanding:
    def test_expansion_mints_typing(self):
        book = stocked()
        author = Author(site="alice")
        author.type_at(0, "start ")
        book.expand_at(author, "sig", 6)
        assert "Best,\nKiruthika" in author.text()

    def test_the_trigger_is_consumed(self):
        book = stocked()
        author = Author(site="alice")
        author.type_at(0, "hello sig")
        book.expand_at(author, "sig", 9, trigger_len=3)
        assert author.text() == "hello Best,\nKiruthika"

    def test_an_unknown_snippet_shows_the_roster(self):
        book = stocked()
        author = Author(site="alice")
        with pytest.raises(Missing) as caught:
            book.expand_at(author, "ghost", 0)
        assert "greet" in str(caught.value)


class TestSharing:
    def test_expansion_converges_on_a_peer(self):
        book = stocked()
        circle = Circle.of(["alice", "bob"])
        ops = book.expand_at(
            circle.author("alice"), "sig", 0
        )
        circle.say("alice", ops)
        circle.settle()
        assert circle.converged() == "Best,\nKiruthika"
