from __future__ import annotations

import pytest

from loom.author import Author
from loom.bulletstyle import bullet_markers, is_uniform, normalize_bullets
from loom.circle import Circle
from loom.errors import Invalid


class TestNormalize:
    def test_mixed_markers_become_uniform(self):
        author = Author(site="alice")
        author.type_at(0, "* a\n+ b\n- c")
        normalize_bullets(author, "-")
        assert author.text() == "- a\n- b\n- c"

    def test_nested_indentation_is_preserved(self):
        author = Author(site="alice")
        author.type_at(0, "  * x")
        normalize_bullets(author, "-")
        assert author.text() == "  - x"

    def test_emphasis_stars_are_not_touched(self):
        author = Author(site="alice")
        author.type_at(0, "text with *bold* word")
        assert normalize_bullets(author, "-") == []

    def test_an_already_uniform_list_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "- a\n- b")
        assert normalize_bullets(author, "-") == []


class TestQueries:
    def test_bullet_markers_are_collected(self):
        author = Author(site="alice")
        author.type_at(0, "* a\n- b")
        assert bullet_markers(author) == {"*", "-"}

    def test_is_uniform_detects_a_mix(self):
        author = Author(site="alice")
        author.type_at(0, "* a\n- b")
        assert not is_uniform(author)


class TestGuard:
    def test_a_bad_marker_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "- a")
        with pytest.raises(Invalid):
            normalize_bullets(author, "x")


class TestConvergence:
    def test_normalization_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "* one\n+ two")
        )
        circle.settle()
        circle.say("alice", normalize_bullets(circle.author("alice"), "-"))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "- one\n- two"
