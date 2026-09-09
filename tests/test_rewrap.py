from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.rewrap import rewrap


class TestRewrap:
    def test_a_paragraph_is_wrapped_to_the_width(self):
        author = Author(site="alice")
        author.type_at(0, "the quick brown fox jumps over the lazy dog")
        rewrap(author, 15)
        assert author.text() == "the quick brown\nfox jumps over\nthe lazy dog"

    def test_a_long_word_is_not_chopped(self):
        author = Author(site="alice")
        author.type_at(0, "supercalifragilistic word")
        rewrap(author, 8)
        assert "supercalifragilistic" in author.text()

    def test_text_already_fitting_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "short line")
        assert rewrap(author, 80) == []


class TestIdentity:
    def test_words_keep_their_strands_across_a_rewrap(self):
        author = Author(site="alice")
        ops = author.type_at(0, "alpha beta gamma delta")
        keep = ops[0].id
        rewrap(author, 11)
        position = author.weave.by_id[keep]
        assert not author.weave.strands[position].sheared
        assert author.weave.strands[position].glyph == "a"


class TestConvergence:
    def test_rewrap_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "one two three four five"),
        )
        circle.settle()
        circle.say("alice", rewrap(circle.author("alice"), 9))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
