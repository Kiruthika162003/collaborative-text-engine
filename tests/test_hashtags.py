from __future__ import annotations

from loom.author import Author
from loom.hashtags import cloud, most_used, tag_counts, tags, unique_tags


class TestFind:
    def test_tags_are_found_and_folded(self):
        author = Author(site="alice")
        author.type_at(0, "on #Draft and #draft topics")
        assert unique_tags(author.weave) == {"draft"}

    def test_a_heading_hash_is_not_a_tag(self):
        author = Author(site="alice")
        author.type_at(0, "# Heading\nbody")
        assert tags(author.weave) == []

    def test_a_bare_number_is_not_a_tag(self):
        author = Author(site="alice")
        author.type_at(0, "issue #123 fixed")
        assert tags(author.weave) == []


class TestCounts:
    def test_tags_are_counted(self):
        author = Author(site="alice")
        author.type_at(0, "#a #b #a #a")
        assert tag_counts(author.weave) == {"a": 3, "b": 1}

    def test_the_most_used_tag_is_named(self):
        author = Author(site="alice")
        author.type_at(0, "#red #blue #red")
        assert most_used(author.weave) == "red"

    def test_an_untagged_document_has_no_most_used(self):
        author = Author(site="alice")
        author.type_at(0, "no tags")
        assert most_used(author.weave) is None


class TestPin:
    def test_a_tag_pins_and_survives_upstream_edits(self):
        author = Author(site="alice")
        author.type_at(0, "see #topic here")
        pin = tags(author.weave)[0].pin
        author.type_at(0, "PRE ")
        assert tags(author.weave)[0].pin == pin


class TestCloud:
    def test_the_cloud_ranks_by_frequency(self):
        author = Author(site="alice")
        author.type_at(0, "#rare #common #common")
        page = cloud(author.weave)
        assert page.splitlines()[0] == "#common (2)"

    def test_an_untagged_document_says_so(self):
        author = Author(site="alice")
        author.type_at(0, "plain prose")
        assert "names no topics" in cloud(author.weave)
