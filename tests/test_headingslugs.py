from __future__ import annotations

from loom.author import Author
from loom.headingslugs import collisions, slug_for, unique_slugs


def repeated() -> Author:
    author = Author(site="alice")
    author.type_at(0, "# Intro\n# Intro\n# Other")
    return author


class TestUnique:
    def test_duplicates_are_disambiguated_in_order(self):
        assert unique_slugs(repeated().weave) == [
            ("Intro", "intro"),
            ("Intro", "intro-1"),
            ("Other", "other"),
        ]

    def test_a_lone_heading_keeps_its_base_slug(self):
        author = Author(site="alice")
        author.type_at(0, "# The Big Idea")
        assert unique_slugs(author.weave) == [("The Big Idea", "the-big-idea")]

    def test_slug_for_indexes_the_list(self):
        assert slug_for(repeated().weave, 1) == "intro-1"


class TestCollisions:
    def test_colliding_bases_are_reported(self):
        assert collisions(repeated().weave) == ["intro"]

    def test_distinct_headings_do_not_collide(self):
        author = Author(site="alice")
        author.type_at(0, "# A\n# B")
        assert collisions(author.weave) == []
