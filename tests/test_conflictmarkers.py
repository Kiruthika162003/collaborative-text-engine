from __future__ import annotations

import pytest

from loom.author import Author
from loom.circle import Circle
from loom.conflictmarkers import (
    conflicts,
    has_conflicts,
    resolve,
    resolve_all,
)
from loom.errors import Invalid

DOC = "a\n<<<<<<< ours\nX\n=======\nY\n>>>>>>> theirs\nb"


def conflicted() -> Author:
    author = Author(site="alice")
    author.type_at(0, DOC)
    return author


class TestParse:
    def test_a_complete_conflict_is_parsed(self):
        found = conflicts(conflicted().weave)
        assert len(found) == 1
        assert found[0].ours == ["X"]
        assert found[0].theirs == ["Y"]

    def test_a_lone_marker_is_not_a_conflict(self):
        author = Author(site="alice")
        author.type_at(0, "talking about <<<<<<< markers here")
        assert conflicts(author.weave) == []

    def test_has_conflicts_reports_presence(self):
        assert has_conflicts(conflicted().weave)
        clean = Author(site="alice")
        clean.type_at(0, "no markers")
        assert not has_conflicts(clean.weave)


class TestResolve:
    def test_picking_ours_keeps_our_side(self):
        author = conflicted()
        resolve(author, 0, "ours")
        assert author.text() == "a\nX\nb"

    def test_picking_theirs_keeps_their_side(self):
        author = conflicted()
        resolve(author, 0, "theirs")
        assert author.text() == "a\nY\nb"

    def test_an_unknown_side_is_refused(self):
        author = conflicted()
        with pytest.raises(Invalid):
            resolve(author, 0, "maybe")


class TestResolveAll:
    def test_all_conflicts_resolve_one_way(self):
        author = Author(site="alice")
        author.type_at(
            0,
            "<<<<<<< ours\nA\n=======\nB\n>>>>>>> theirs\n"
            "mid\n"
            "<<<<<<< ours\nC\n=======\nD\n>>>>>>> theirs",
        )
        resolve_all(author, "ours")
        assert not has_conflicts(author.weave)
        assert "A" in author.text()
        assert "C" in author.text()
        assert "B" not in author.text()


class TestConvergence:
    def test_resolution_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, DOC)
        )
        circle.settle()
        circle.say("alice", resolve(circle.author("alice"), 0, "ours"))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert circle.converged() == "a\nX\nb"
