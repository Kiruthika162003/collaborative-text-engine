from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.dedupe import dedupe_lines, deduped_text


class TestDedupe:
    def test_an_adjacent_duplicate_is_removed(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb\nb\nc")
        dedupe_lines(author)
        assert author.text() == "a\nb\nc"

    def test_a_non_adjacent_repeat_is_kept(self):
        author = Author(site="alice")
        author.type_at(0, "a\nb\na")
        assert dedupe_lines(author) == []

    def test_blank_lines_are_not_deduped(self):
        author = Author(site="alice")
        author.type_at(0, "x\n\n\ny")
        assert dedupe_lines(author) == []

    def test_a_triple_collapses_to_one(self):
        author = Author(site="alice")
        author.type_at(0, "row\nrow\nrow")
        dedupe_lines(author)
        assert author.text() == "row"


class TestPure:
    def test_deduped_text_is_pure(self):
        assert deduped_text("a\na\nb") == "a\nb"


class TestConvergence:
    def test_dedupe_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "keep\nsame\nsame\ndone"),
        )
        circle.settle()
        circle.say("alice", dedupe_lines(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "keep\nsame\ndone"
