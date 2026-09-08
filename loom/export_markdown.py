"""Markdown export: the dressed cloth rendered to text a plain editor reads.

A collaborative document with bold and italic marks is
useless if it can only be read inside the loom, so this
module renders the fabric and its wardrobe to Markdown, the
lingua franca of plain-text formatting. It walks the visible
spans the wardrobe already computes, wrapping bold in double
stars and italic in single, and nests them in the one order
Markdown tolerates so bold italic reads as triple stars
rather than a tag salad. Styles the exporter does not know
are not invented into syntax; they are dropped from the
output with their names collected into a footnote, because
silently discarding a style is how a heading becomes a
paragraph in the version someone actually ships, and a
loud footnote is a bug report the reader can act on. Marks
that begin or end on a sheared strand are honored by their
surviving glyphs, the export reading the wardrobe's spans
rather than re-deriving them, because there is exactly one
correct span computation in this codebase and this is not
the place to write a second.
"""

from __future__ import annotations

from loom.marks import Wardrobe

KNOWN_STYLES = ("bold", "italic")
MARKERS = {"bold": "**", "italic": "*"}


def to_markdown(wardrobe: Wardrobe) -> str:
    parts = []
    dropped: set = set()
    for text, styles in wardrobe.spans():
        known = [
            style
            for style in ("bold", "italic")
            if style in styles
        ]
        for style in styles:
            if style not in KNOWN_STYLES:
                dropped.add(style)
        wrap = "".join(
            MARKERS[style] for style in known
        )
        if wrap and text.strip():
            parts.append(f"{wrap}{text}{wrap}")
        else:
            parts.append(text)
    body = "".join(parts)
    if dropped:
        footnote = ", ".join(sorted(dropped))
        return (
            f"{body}\n\n[unexported styles dropped: "
            f"{footnote}; a silently discarded style "
            "is how a heading becomes a paragraph]"
        )
    return body


def unknown_styles(wardrobe: Wardrobe) -> list[str]:
    found: set = set()
    for _text, styles in wardrobe.spans():
        for style in styles:
            if style not in KNOWN_STYLES:
                found.add(style)
    return sorted(found)
