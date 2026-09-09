from __future__ import annotations

from loom.author import Author
from loom.circle import Circle
from loom.frontmatter import get
from loom.frontmatterwrite import remove_field, set_field


class TestSet:
    def test_an_existing_field_is_replaced(self):
        author = Author(site="alice")
        author.type_at(0, "---\ntitle: Old\n---\nbody")
        set_field(author, "title", "New")
        assert get(author.weave, "title") == "New"
        assert author.text().endswith("---\nbody")

    def test_a_new_field_is_added_to_the_block(self):
        author = Author(site="alice")
        author.type_at(0, "---\ntitle: Old\n---\nbody")
        set_field(author, "author", "alice")
        assert get(author.weave, "author") == "alice"
        assert get(author.weave, "title") == "Old"

    def test_a_block_is_created_when_absent(self):
        author = Author(site="alice")
        author.type_at(0, "just body")
        set_field(author, "title", "X")
        assert author.text() == "---\ntitle: X\n---\njust body"


class TestRemove:
    def test_a_field_is_removed(self):
        author = Author(site="alice")
        author.type_at(0, "---\ntitle: T\nauthor: a\n---\nbody")
        remove_field(author, "title")
        assert get(author.weave, "title") == ""
        assert get(author.weave, "author") == "a"

    def test_removing_an_absent_field_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "---\ntitle: T\n---\nbody")
        assert remove_field(author, "ghost") == []

    def test_removing_from_a_plain_document_mints_nothing(self):
        author = Author(site="alice")
        author.type_at(0, "no front matter")
        assert remove_field(author, "title") == []


class TestConvergence:
    def test_setting_a_field_converges_across_a_circle(self):
        circle = Circle.of(["alice", "bob"])
        circle.say(
            "alice", circle.author("alice").type_at(0, "body only")
        )
        circle.settle()
        circle.say("alice", set_field(circle.author("alice"), "k", "v"))
        circle.settle()
        assert circle.converged() == circle.author("bob").text()
        assert get(circle.author("bob").weave, "k") == "v"
