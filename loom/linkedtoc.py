"""Linked contents: a nested list of headings, each a link to its unique anchor.

The toc module numbers a contents and the toc-tool inserts one
between markers; this renders the third form a document wants,
a nested bullet list where each heading is a Markdown link to
its own anchor, the clickable contents a rendered page carries
at the top. It draws the nesting from the heading tree, so a
subsection sits indented under its section, and it links to the
unique slug the heading-slugs module computes, so two headings
that share a title link to two different anchors rather than
both to the first. Those two organs do the hard parts, the tree
its indentation and the slugs their disambiguation, and this
only joins them into the list a reader clicks, which is the
value of building it here rather than in either: neither the
tree nor the slugs should know about Markdown link syntax, and
this is the one place that does. It renders and inserts nothing,
because a linked contents is often kept in a separate navigation
pane or prepended by the toc-tool that owns in-place insertion;
this produces the text and leaves where it goes to the caller. A
document with no headings has no contents to link and says so,
rather than emitting an empty list that implies the headings
were lost rather than never there.
"""

from __future__ import annotations

from loom.headingslugs import unique_slugs
from loom.treeoutline import visible_nodes
from loom.weave import Weave


def linked_toc(weave: Weave) -> str:
    nodes = visible_nodes(weave)
    slugs = [slug for _title, slug in unique_slugs(weave)]
    if not nodes:
        return "no headings; no contents to link"
    lines = []
    for (node, depth), slug in zip(nodes, slugs, strict=True):
        indent = "  " * depth
        lines.append(f"{indent}- [{node.heading.title}](#{slug})")
    return "\n".join(lines)
