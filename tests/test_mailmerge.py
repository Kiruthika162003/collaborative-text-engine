from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.mailmerge import fields, fill, merge, merge_from_frontmatter, unfilled


class TestFill:
    def test_placeholders_are_replaced(self):
        assert fill("Dear {{name}}, hi", {"name": "Al"}) == "Dear Al, hi"

    def test_an_unknown_placeholder_is_left_standing(self):
        assert fill("Dear {{ghost}}", {}) == "Dear {{ghost}}"

    def test_a_stray_brace_is_not_a_field(self):
        assert fill("a { b } c", {"b": "X"}) == "a { b } c"


class TestFields:
    def test_fields_are_listed_in_order(self):
        assert fields("{{a}} and {{b}} and {{a}}") == ["a", "b"]

    def test_unfilled_names_the_missing(self):
        assert unfilled("{{a}} {{b}}", {"a": "1"}) == ["b"]


class TestMerge:
    def test_merge_reaches_the_filled_text(self):
        author = Author(site="alice")
        author.type_at(0, "total is {{n}}")
        merge(author, {"n": "5"})
        assert author.text() == "total is 5"

    def test_merge_from_frontmatter_uses_the_block(self):
        author = Author(site="alice")
        author.type_at(0, "---\nname: Al\n---\nDear {{name}}")
        merge_from_frontmatter(author)
        assert author.text().endswith("Dear Al")


class TestConvergence:
    def test_merge_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "hi {{who}}")
        )
        circle.settle()
        circle.say("alice", merge(circle.author("alice"), {"who": "bob"}))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "hi bob"
