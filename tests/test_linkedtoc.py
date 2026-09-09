from __future__ import annotations

from loom.author import Author
from loom.linkedtoc import linked_toc


class TestLinkedToc:
    def test_a_nested_contents_links_each_heading(self):
        author = Author(site="alice")
        author.type_at(0, "# One\n## Two\n# Three")
        assert linked_toc(author.weave) == (
            "- [One](#one)\n  - [Two](#two)\n- [Three](#three)"
        )

    def test_duplicate_titles_get_distinct_anchors(self):
        author = Author(site="alice")
        author.type_at(0, "# Intro\n# Intro")
        toc = linked_toc(author.weave)
        assert "(#intro)" in toc
        assert "(#intro-1)" in toc

    def test_depth_indents_the_link(self):
        author = Author(site="alice")
        author.type_at(0, "# A\n## B\n### C")
        lines = linked_toc(author.weave).splitlines()
        assert lines[2].startswith("    - [C]")

    def test_a_flat_document_has_no_contents(self):
        author = Author(site="alice")
        author.type_at(0, "no headings here")
        assert "no contents" in linked_toc(author.weave)
