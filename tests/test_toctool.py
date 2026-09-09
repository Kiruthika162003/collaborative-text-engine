from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.toctool import CLOSE, OPEN, has_toc, insert_toc


def documented() -> Author:
    author = Author(site="alice")
    author.type_at(0, "# A\n## B\nbody")
    return author


class TestInsert:
    def test_a_toc_is_prepended_with_markers(self):
        author = documented()
        insert_toc(author)
        assert author.text().startswith(OPEN)
        assert "- A\n  - B" in author.text()
        assert CLOSE in author.text()

    def test_the_body_is_preserved_below(self):
        author = documented()
        insert_toc(author)
        assert author.text().endswith("# A\n## B\nbody")

    def test_a_placeholder_open_marker_expands(self):
        author = Author(site="alice")
        author.type_at(0, "intro\n<!-- toc -->\n# A")
        insert_toc(author)
        assert has_toc(author.weave)
        assert "- A" in author.text()


class TestRegenerate:
    def test_regenerating_replaces_not_stacks(self):
        author = documented()
        insert_toc(author)
        insert_toc(author)
        assert author.text().count(OPEN) == 1
        assert author.text().count(CLOSE) == 1

    def test_a_new_heading_appears_on_regenerate(self):
        author = documented()
        insert_toc(author)
        author.type_at(author.weave.visible_count(), "\n# C")
        insert_toc(author)
        assert "- C" in author.text()

    def test_regeneration_is_idempotent_when_unchanged(self):
        author = documented()
        insert_toc(author)
        before = author.text()
        assert insert_toc(author) == []
        assert author.text() == before


class TestConvergence:
    def test_toc_insertion_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice",
            circle.author("alice").type_at(0, "# One\n## Two"),
        )
        circle.settle()
        circle.say("alice", insert_toc(circle.author("alice")))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert OPEN in circle.converged()
