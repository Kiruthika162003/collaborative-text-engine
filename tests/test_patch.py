from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.patch import patch, would_change


class TestPatch:
    def test_a_replace_reaches_the_target(self):
        author = Author(site="alice")
        author.type_at(0, "hello world")
        patch(author, "hello there")
        assert author.text() == "hello there"

    def test_an_insert_reaches_the_target(self):
        author = Author(site="alice")
        author.type_at(0, "abc")
        patch(author, "abXc")
        assert author.text() == "abXc"

    def test_a_delete_reaches_the_target(self):
        author = Author(site="alice")
        author.type_at(0, "abc")
        patch(author, "ac")
        assert author.text() == "ac"

    def test_matching_text_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "same")
        assert patch(author, "same") == []


class TestIdentity:
    def test_unchanged_glyphs_keep_their_strands(self):
        author = Author(site="alice")
        ops = author.type_at(0, "hello world")
        keep = ops[0].id
        patch(author, "hello there")
        position = author.weave.by_id[keep]
        assert not author.weave.strands[position].sheared
        assert author.weave.strands[position].glyph == "h"


class TestQuery:
    def test_would_change_detects_a_difference(self):
        author = Author(site="alice")
        author.type_at(0, "one")
        assert would_change(author, "two")
        assert not would_change(author, "one")


class TestConvergence:
    def test_a_patch_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "draft one")
        )
        circle.settle()
        circle.say("alice", patch(circle.author("alice"), "draft two"))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "draft two"
