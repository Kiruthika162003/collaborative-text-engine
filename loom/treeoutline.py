"""Tree outline: the flat heading list built into the nesting it implies, with folds.

The headings module reads a flat list with a level on each;
this builds that list into the tree the levels describe, so
a navigator can show a section with its subsections tucked
under it and fold a branch closed the way every outliner
does. The tree is built by the same rule the flat outline
nests by, each heading hanging off the nearest preceding
heading of a shallower level, and a heading that skipped a
level is attached to that nearest shallower ancestor rather
than given an invented parent, because inventing a node to
fill a gap would put a heading in the outline that the
writer never typed. Folding is the tree's own trick: given a
set of collapsed headings, the walk yields each node with
its depth but skips the descendants of anything folded, so a
long document shows as its top-level sections until a reader
opens one, and the fold is keyed by the heading's strand pin
so a branch stays folded across the edits that shift its
line. The tree is recomputed from the living headings every
time rather than stored, because the outline is a view of
the text and the text is what moves, and a cached tree is a
map that quietly stops matching its territory.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.headings import Heading, headings
from loom.ids import OpId
from loom.weave import Weave


@dataclass
class Node:
    heading: Heading
    children: list[Node] = field(default_factory=list)


def tree(weave: Weave) -> list[Node]:
    roots: list[Node] = []
    stack: list[Node] = []
    for heading in headings(weave):
        node = Node(heading=heading)
        while stack and stack[-1].heading.level >= heading.level:
            stack.pop()
        if stack:
            stack[-1].children.append(node)
        else:
            roots.append(node)
        stack.append(node)
    return roots


def flatten(nodes: list[Node]) -> list[Node]:
    order: list[Node] = []
    for node in nodes:
        order.append(node)
        order.extend(flatten(node.children))
    return order


def descendant_count(node: Node) -> int:
    return sum(1 + descendant_count(child) for child in node.children)


def visible_nodes(
    weave: Weave, collapsed: frozenset[OpId] = frozenset()
) -> list[tuple[Node, int]]:
    result: list[tuple[Node, int]] = []

    def walk(nodes: list[Node], depth: int) -> None:
        for node in nodes:
            result.append((node, depth))
            if node.heading.pin not in collapsed:
                walk(node.children, depth + 1)

    walk(tree(weave), 0)
    return result


def render_tree(
    weave: Weave, collapsed: frozenset[OpId] = frozenset()
) -> str:
    visible = visible_nodes(weave, collapsed)
    if not visible:
        return "no headings; the outline has no tree"
    lines = []
    for node, depth in visible:
        folded = (
            " [+]"
            if node.heading.pin in collapsed and node.children
            else ""
        )
        lines.append("  " * depth + node.heading.title + folded)
    return "\n".join(lines)
