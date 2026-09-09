from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.tablesort import sort_table

TABLE = "| name | age |\n| - | - |\n| Al | 30 |\n| Bob | 5 |"


class TestSort:
    def test_a_numeric_column_sorts_numerically(self):
        author = Author(site="alice")
        author.type_at(0, TABLE)
        sort_table(author, 1)
        rows = author.text().splitlines()
        assert rows[2].startswith("| Bob")
        assert rows[3].startswith("| Al")

    def test_a_text_column_sorts_lexically(self):
        author = Author(site="alice")
        author.type_at(0, "| a |\n| - |\n| banana |\n| apple |")
        sort_table(author, 0)
        rows = author.text().splitlines()
        assert "apple" in rows[2]
        assert "banana" in rows[3]

    def test_reverse_sorts_descending(self):
        author = Author(site="alice")
        author.type_at(0, TABLE)
        sort_table(author, 1, reverse=True)
        rows = author.text().splitlines()
        assert rows[2].startswith("| Al")

    def test_an_already_sorted_and_formatted_table_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "| n   |\n| --- |\n| 1   |\n| 2   |")
        assert sort_table(author, 0) == []


class TestConvergence:
    def test_sorting_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, TABLE),
        )
        circle.settle()
        circle.say("alice", sort_table(circle.author("alice"), 1))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "Bob" in circle.converged().splitlines()[2]
