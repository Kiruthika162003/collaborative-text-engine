from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.tabs import expand_tabs, expanded_text, has_tabs


class TestExpand:
    def test_a_leading_tab_fills_to_the_stop(self):
        author = Author(site="alice")
        author.type_at(0, "\tx")
        expand_tabs(author, 4)
        assert author.text() == "    x"

    def test_a_mid_line_tab_fills_only_to_the_next_stop(self):
        author = Author(site="alice")
        author.type_at(0, "a\tb")
        expand_tabs(author, 4)
        assert author.text() == "a   b"

    def test_the_width_is_honoured(self):
        author = Author(site="alice")
        author.type_at(0, "\tx")
        expand_tabs(author, 2)
        assert author.text() == "  x"

    def test_a_tabless_document_is_unchanged(self):
        author = Author(site="alice")
        author.type_at(0, "no tabs here")
        assert expand_tabs(author) == []


class TestPure:
    def test_expanded_text_is_a_pure_function(self):
        assert expanded_text("a\tb", 4) == "a   b"

    def test_has_tabs_detects_a_tab(self):
        assert has_tabs("a\tb")
        assert not has_tabs("a b")


class TestConvergence:
    def test_expansion_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "a\tb\tc")
        )
        circle.settle()
        circle.say("alice", expand_tabs(circle.author("alice"), 4))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "\t" not in circle.converged()
