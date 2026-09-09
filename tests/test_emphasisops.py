from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.emphasisops import bold, code, italic, strike, wrap
from loom.errors import Invalid


class TestWrap:
    def test_bold_wraps_the_range(self):
        author = Author(site="alice")
        author.type_at(0, "the quick brown")
        bold(author, 4, 5)
        assert author.text() == "the **quick** brown"

    def test_italic_wraps_the_range(self):
        author = Author(site="alice")
        author.type_at(0, "the quick brown")
        italic(author, 4, 5)
        assert author.text() == "the *quick* brown"

    def test_code_wraps_the_range(self):
        author = Author(site="alice")
        author.type_at(0, "run this now")
        code(author, 4, 4)
        assert author.text() == "run `this` now"

    def test_strike_wraps_the_range(self):
        author = Author(site="alice")
        author.type_at(0, "keep drop it")
        strike(author, 5, 4)
        assert author.text() == "keep ~~drop~~ it"


class TestEdges:
    def test_wrapping_at_the_end_appends_the_marker(self):
        author = Author(site="alice")
        author.type_at(0, "final word")
        bold(author, 6, 4)
        assert author.text() == "final **word**"

    def test_wrapping_zero_glyphs_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "x")
        with pytest.raises(Invalid):
            wrap(author, 0, 0, "*")


class TestConvergence:
    def test_emphasis_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "make bold here"),
        )
        circle.settle()
        circle.say("alice", bold(circle.author("alice"), 5, 4))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "**bold**" in circle.converged()
