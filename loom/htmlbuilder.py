"""HTML builder: assemble a tree of HTML elements and render it, everything escaped.

Where the HTML-render module turns Markdown into HTML, this
builds HTML directly, an element at a time, for a caller
generating markup from data rather than from prose. An element
has a tag, attributes, and children that are other elements or
text, and it renders to the nested markup, opening and closing
tags around the rendered children. The safety rule is absolute
and built in: text children are escaped and attribute values
are escaped, so a caller can put arbitrary data into the tree
without it becoming markup, the one guarantee an HTML builder
must never let a caller forget, because a builder that emitted
unescaped text would make every value a potential injection.
Void elements, the ones HTML forbids a closing tag on, br and
img and their kind, render as a single self-standing tag with
no children rendered, so a caller who adds a child to a void
element gets the void element rather than invalid markup with
a close tag HTML rejects. The building calls return the element
so a tree builds in a chained expression, and elements are held
as a tree until render, so a caller can build once and render
many times. It renders and holds no layout opinion, no
pretty-printing indentation, because whitespace between HTML
elements is sometimes significant and a builder that added it
would change the rendered result; a caller who wants it
readable can pass the output through a formatter that knows
which whitespace is safe to add.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.htmlescape import escape

VOID = frozenset(
    {"br", "img", "hr", "input", "meta", "link", "area", "base", "col", "source"}
)


@dataclass
class Element:
    tag: str
    attributes: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def attr(self, key: str, value: str) -> Element:
        self.attributes[key] = value
        return self

    def add(self, child: Element | str) -> Element:
        self.children.append(child)
        return self

    def _attrs(self) -> str:
        return "".join(
            f' {key}="{escape(str(value))}"'
            for key, value in self.attributes.items()
        )

    def render(self) -> str:
        opening = f"<{self.tag}{self._attrs()}>"
        if self.tag in VOID:
            return opening
        inner = "".join(
            child.render() if isinstance(child, Element) else escape(child)
            for child in self.children
        )
        return f"{opening}{inner}</{self.tag}>"


def element(tag: str, **attributes: str) -> Element:
    return Element(tag=tag, attributes=dict(attributes))
