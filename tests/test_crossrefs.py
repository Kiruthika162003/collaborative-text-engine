from __future__ import annotations

from loom.author import Author
from loom.crossrefs import (
    ambiguous,
    broken,
    crossrefs,
    orphans,
    report,
    slugify,
)


def linked() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "# Intro\nSee [the method](#method) below.\n"
        "# Method\nAs [[Intro]] said.\n# Lonely",
    )
    return author


class TestSlugify:
    def test_spaces_become_hyphens_and_case_folds(self):
        assert slugify("The Big Idea") == "the-big-idea"

    def test_punctuation_is_dropped(self):
        assert slugify("What? Now!") == "what-now"


class TestResolve:
    def test_a_link_to_a_heading_resolves(self):
        refs = crossrefs(linked().weave)
        method = next(r for r in refs if r.target == "method")
        assert method.resolved

    def test_a_wiki_link_resolves_by_slug(self):
        refs = crossrefs(linked().weave)
        assert any(r.target == "intro" and r.resolved for r in refs)

    def test_a_link_to_nothing_is_broken(self):
        author = Author(site="alice")
        author.type_at(0, "# Real\nsee [ghost](#ghost)")
        assert [r.target for r in broken(author.weave)] == ["ghost"]


class TestOrphans:
    def test_an_unlinked_heading_is_an_orphan(self):
        assert "lonely" in orphans(linked().weave)

    def test_a_linked_heading_is_not_an_orphan(self):
        assert "method" not in orphans(linked().weave)


class TestAmbiguous:
    def test_two_headings_with_one_slug_are_ambiguous(self):
        author = Author(site="alice")
        author.type_at(0, "# Notes\n# Notes")
        assert ambiguous(author.weave) == ["notes"]


class TestReport:
    def test_the_report_counts_links_and_broken(self):
        author = Author(site="alice")
        author.type_at(0, "# A\n[to a](#a) and [to x](#x)")
        page = report(author.weave)
        assert "2 internal link(s), 1 broken" in page

    def test_a_bare_document_has_nothing_to_reference(self):
        author = Author(site="alice")
        author.type_at(0, "just prose")
        assert "nothing to cross-reference" in report(author.weave)
