from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.tableformat import format_tables, formatted_text

MESSY = "intro\n|a|b|\n|-|-|\n|1|22|\nend"
TIDY = "intro\n| a   | b   |\n| --- | --- |\n| 1   | 22  |\nend"


class TestFormat:
    def test_a_messy_table_is_tidied(self):
        author = Author(site="alice")
        author.type_at(0, MESSY)
        format_tables(author)
        assert author.text() == TIDY

    def test_surrounding_prose_is_preserved(self):
        author = Author(site="alice")
        author.type_at(0, MESSY)
        format_tables(author)
        assert author.text().startswith("intro\n")
        assert author.text().endswith("\nend")

    def test_an_already_tidy_table_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, TIDY)
        assert format_tables(author) == []

    def test_prose_with_pipes_is_not_a_table(self):
        author = Author(site="alice")
        author.type_at(0, "a | b but no separator row")
        assert format_tables(author) == []


class TestPure:
    def test_formatted_text_is_pure(self):
        assert formatted_text(MESSY) == TIDY


class TestConvergence:
    def test_formatting_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "|x|y|\n|-|-|\n|1|2|"),
        )
        circle.settle()
        circle.say("alice", format_tables(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "| x   | y   |" in circle.converged()
