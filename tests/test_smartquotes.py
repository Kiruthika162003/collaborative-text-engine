from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.smartquotes import (
    LEFT_DOUBLE,
    LEFT_SINGLE,
    RIGHT_DOUBLE,
    RIGHT_SINGLE,
    curl,
)


def _whole(author: Author):
    return curl(author, 0, author.weave.visible_count())


class TestDouble:
    def test_a_quoted_phrase_gets_matching_curls(self):
        author = Author(site="alice")
        author.type_at(0, 'say "hi" now')
        _whole(author)
        assert LEFT_DOUBLE + "hi" + RIGHT_DOUBLE in author.text()

    def test_an_opening_quote_after_a_bracket_opens(self):
        author = Author(site="alice")
        author.type_at(0, '("x")')
        _whole(author)
        assert author.text().startswith("(" + LEFT_DOUBLE)


class TestSingle:
    def test_an_apostrophe_between_letters_is_a_right_single(self):
        author = Author(site="alice")
        author.type_at(0, "don't")
        _whole(author)
        assert author.text() == "don" + RIGHT_SINGLE + "t"

    def test_a_leading_apostrophe_is_curled_wrong(self):
        # 'tis should take a right single quote for the
        # dropped letters; the space-before rule opens it
        # instead, a named failure kept rather than hidden
        author = Author(site="alice")
        author.type_at(0, "say 'tis")
        _whole(author)
        assert author.text().endswith(LEFT_SINGLE + "tis")


class TestTouch:
    def test_only_quote_glyphs_change(self):
        author = Author(site="alice")
        ops = author.type_at(0, 'a "b"')
        keep = ops[0].id
        result = curl(author, 0, 5)
        assert result.curled == 2
        position = author.weave.by_id[keep]
        assert not author.weave.strands[position].sheared

    def test_prose_without_quotes_curls_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "plain prose")
        result = _whole(author)
        assert result.curled == 0
        assert result.ops == []


class TestConvergence:
    def test_curling_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, 'she said "go"'),
        )
        circle.settle()
        result = curl(
            circle.author("alice"),
            0,
            circle.author("alice").weave.visible_count(),
        )
        circle.say("alice", result.ops)
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert LEFT_DOUBLE in circle.converged()
