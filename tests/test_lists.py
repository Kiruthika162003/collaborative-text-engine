from __future__ import annotations

from loom.author import Author
from loom.lists import deepest, items, render


def numbered() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "1. first\n5. second\n  9. nested a\n"
        "  9. nested b\n3. third",
    )
    return author


class TestRenumbering:
    def test_typed_numbers_are_recomputed(self):
        author = numbered()
        page = render(author.weave)
        lines = page.split("\n")
        assert lines[0] == "1. first"
        assert lines[1] == "2. second"
        assert lines[4] == "3. third"

    def test_nested_lists_restart_their_count(self):
        author = numbered()
        page = render(author.weave)
        assert "  1. nested a" in page
        assert "  2. nested b" in page

    def test_depth_comes_from_leading_spaces(self):
        author = numbered()
        assert deepest(author.weave) == 2


class TestBullets:
    def test_dashes_are_bullets(self):
        author = Author(site="alice")
        author.type_at(0, "- one\n- two")
        found = items(author.weave)
        assert all(i.kind == "bullet" for i in found)
        assert render(author.weave) == "- one\n- two"

    def test_a_paragraph_breaks_the_list(self):
        author = Author(site="alice")
        author.type_at(0, "- a\n- b\n\n- c")
        numbers = [i.number for i in items(author.weave)]
        assert numbers == [1, 2, 1]


class TestEmpty:
    def test_prose_has_no_items(self):
        author = Author(site="alice")
        author.type_at(0, "just a sentence")
        assert items(author.weave) == []
        assert "no list items" in render(author.weave)
