from __future__ import annotations

from loom.author import Author
from loom.headings import headings
from loom.ids import OpId
from loom.treeoutline import (
    descendant_count,
    flatten,
    render_tree,
    tree,
    visible_nodes,
)


def doc() -> Author:
    author = Author(site="alice")
    author.type_at(
        0,
        "# One\n## One A\n### Deep\n## One B\n# Two",
    )
    return author


def pin_of(author: Author, title: str) -> OpId:
    return next(h.pin for h in headings(author.weave) if h.title == title)


class TestTree:
    def test_children_hang_under_their_parent(self):
        roots = tree(doc().weave)
        assert [r.heading.title for r in roots] == ["One", "Two"]
        assert [c.heading.title for c in roots[0].children] == [
            "One A",
            "One B",
        ]

    def test_a_deep_heading_nests_under_its_section(self):
        roots = tree(doc().weave)
        one_a = roots[0].children[0]
        assert [c.heading.title for c in one_a.children] == ["Deep"]

    def test_flatten_returns_reading_order(self):
        titles = [n.heading.title for n in flatten(tree(doc().weave))]
        assert titles == ["One", "One A", "Deep", "One B", "Two"]

    def test_descendant_count_walks_the_branch(self):
        roots = tree(doc().weave)
        assert descendant_count(roots[0]) == 3


class TestFold:
    def test_folding_hides_descendants(self):
        author = doc()
        collapsed = frozenset({pin_of(author, "One")})
        visible = [
            n.heading.title
            for n, _depth in visible_nodes(author.weave, collapsed)
        ]
        assert visible == ["One", "Two"]

    def test_an_unfolded_tree_shows_everything(self):
        author = doc()
        visible = visible_nodes(author.weave)
        assert len(visible) == 5


class TestRender:
    def test_render_indents_by_depth(self):
        page = render_tree(doc().weave)
        assert "    Deep" in page
        assert "  One A" in page

    def test_a_folded_branch_is_marked(self):
        author = doc()
        collapsed = frozenset({pin_of(author, "One")})
        page = render_tree(author.weave, collapsed)
        assert "One [+]" in page

    def test_a_flat_document_has_no_tree(self):
        author = Author(site="alice")
        author.type_at(0, "no headings here")
        assert "no tree" in render_tree(author.weave)
