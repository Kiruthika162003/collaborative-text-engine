from __future__ import annotations

from loom.author import Author
from loom.casing import lower, sentence, title, upper
from loom.circle import Circle


class TestUpper:
    def test_upper_raises_the_range(self):
        author = Author(site="alice")
        author.type_at(0, "hello world")
        upper(author, 0, 5)
        assert author.text() == "HELLO world"

    def test_upper_touches_only_glyphs_that_change(self):
        author = Author(site="alice")
        ops = author.type_at(0, "aBc")
        keep = ops[1].id
        result = upper(author, 0, 3)
        assert result.changed == 2
        position = author.weave.by_id[keep]
        strand = author.weave.strands[position]
        assert not strand.sheared
        assert strand.glyph == "B"
        assert author.text() == "ABC"


class TestLower:
    def test_lower_drops_the_range(self):
        author = Author(site="alice")
        author.type_at(0, "SHOUT quietly")
        lower(author, 0, 5)
        assert author.text() == "shout quietly"


class TestTitle:
    def test_title_capitalizes_word_starts(self):
        author = Author(site="alice")
        author.type_at(0, "the quick fox")
        title(author, 0, 13)
        assert author.text() == "The Quick Fox"

    def test_a_range_beginning_mid_word_is_not_capitalized(self):
        author = Author(site="alice")
        author.type_at(0, "internet")
        result = title(author, 4, 4)
        assert result.changed == 0
        assert author.text() == "internet"


class TestSentence:
    def test_sentence_capitalizes_each_sentence_start(self):
        author = Author(site="alice")
        author.type_at(0, "hello. world here")
        sentence(author, 0, 17)
        assert author.text() == "Hello. World here"

    def test_a_range_after_a_period_opens_with_a_capital(self):
        author = Author(site="alice")
        author.type_at(0, "done. next")
        sentence(author, 6, 4)
        assert author.text() == "done. Next"


class TestNoop:
    def test_a_transform_that_changes_nothing_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "ALL CAPS")
        result = upper(author, 0, 8)
        assert result.changed == 0
        assert result.ops == []


class TestConvergence:
    def test_a_case_change_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "quiet word"),
        )
        circle.settle()
        result = upper(circle.author("alice"), 0, 5)
        circle.say("alice", result.ops)
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged().startswith("QUIET")
