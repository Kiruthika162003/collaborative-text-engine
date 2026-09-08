from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.errors import Invalid, Missing
from loom.headings import headings
from loom.ids import OpId
from loom.nesting import (
    demote,
    demote_subtree,
    level_at,
    promote,
    promote_subtree,
)


def tree() -> Author:
    author = Author(site="alice")
    author.type_at(0, "# Top\n## Child\n### Grand\n## Sibling")
    return author


def pin_of(author: Author, title: str) -> OpId:
    return next(h.pin for h in headings(author.weave) if h.title == title)


class TestSingle:
    def test_promote_removes_a_hash(self):
        author = tree()
        promote(author, pin_of(author, "Child"))
        assert level_at(author.weave, pin_of(author, "Child")) == 1

    def test_demote_adds_a_hash(self):
        author = tree()
        demote(author, pin_of(author, "Top"))
        assert level_at(author.weave, pin_of(author, "Top")) == 2

    def test_promoting_a_top_heading_is_refused(self):
        author = tree()
        with pytest.raises(Invalid):
            promote(author, pin_of(author, "Top"))

    def test_demoting_a_level_six_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "###### Deep")
        with pytest.raises(Invalid):
            demote(author, pin_of(author, "Deep"))


class TestSubtree:
    def test_promote_subtree_shifts_the_children(self):
        author = tree()
        promote_subtree(author, pin_of(author, "Child"))
        assert level_at(author.weave, pin_of(author, "Child")) == 1
        assert level_at(author.weave, pin_of(author, "Grand")) == 2
        assert level_at(author.weave, pin_of(author, "Sibling")) == 2

    def test_demote_subtree_shifts_the_children(self):
        author = tree()
        demote_subtree(author, pin_of(author, "Child"))
        assert level_at(author.weave, pin_of(author, "Child")) == 3
        assert level_at(author.weave, pin_of(author, "Grand")) == 4

    def test_a_subtree_refuses_whole_when_a_member_is_top(self):
        author = Author(site="alice")
        author.type_at(0, "# A\n## B")
        with pytest.raises(Invalid):
            promote_subtree(author, pin_of(author, "A"))


class TestGuards:
    def test_nesting_a_line_of_prose_is_refused(self):
        author = Author(site="alice")
        ops = author.type_at(0, "just prose\n## Head")
        with pytest.raises(Missing):
            promote(author, ops[0].id)


class TestConvergence:
    def test_a_promotion_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "# One\n## Two"),
        )
        circle.settle()
        pin = next(
            h.pin
            for h in headings(circle.author("alice").weave)
            if h.title == "Two"
        )
        circle.say("alice", promote(circle.author("alice"), pin))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert "# Two" in circle.converged()
