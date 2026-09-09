"""Markdown builder: assemble a Markdown document from blocks, then render it.

Generating a Markdown document from data, a report, a summary,
a changelog, wants a builder that speaks in blocks rather than
string concatenation, and this is that: a fluent sequence of
heading, paragraph, bullet list, numbered list, code block, and
blockquote calls that render to well-formed Markdown with the
blank lines between blocks that the format needs. The value
over building the string by hand is that the spacing is correct
by construction, one blank line between every pair of blocks
and none inside a list, which is the rule a hand-built string
gets wrong the third time it is edited. Each call returns the
builder so a document builds in one chained expression that
reads top to bottom the way the document does. A heading's
level is validated to the one-through-six Markdown allows,
because a heading of level zero or seven is not a heading any
renderer honours and refusing it points at the mistake rather
than emitting markup that silently does nothing. The blocks are
kept as data until render, so a caller can build and re-render,
and the render is the one place that knows Markdown's block
syntax, so the builder's callers describe structure and this
translates it, which is the separation that lets the same
document render to something other than Markdown later by
swapping only the renderer. It builds and renders and holds no
opinion about where the text goes, since that is the caller's.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid


@dataclass
class MarkdownBuilder:
    blocks: list[tuple] = field(default_factory=list)

    def heading(self, level: int, title: str) -> MarkdownBuilder:
        if not 1 <= level <= 6:
            raise Invalid("a heading level runs from one to six")
        self.blocks.append(("heading", level, title))
        return self

    def paragraph(self, text: str) -> MarkdownBuilder:
        self.blocks.append(("paragraph", text))
        return self

    def bullets(self, items: list[str]) -> MarkdownBuilder:
        self.blocks.append(("bullets", items))
        return self

    def numbered(self, items: list[str]) -> MarkdownBuilder:
        self.blocks.append(("numbered", items))
        return self

    def code(self, body: str, language: str = "") -> MarkdownBuilder:
        self.blocks.append(("code", body, language))
        return self

    def quote(self, text: str) -> MarkdownBuilder:
        self.blocks.append(("quote", text))
        return self

    def _render_block(self, block: tuple) -> str:
        kind = block[0]
        if kind == "heading":
            return "#" * block[1] + " " + block[2]
        if kind == "paragraph":
            return block[1]
        if kind == "bullets":
            return "\n".join(f"- {item}" for item in block[1])
        if kind == "numbered":
            return "\n".join(
                f"{number}. {item}"
                for number, item in enumerate(block[1], start=1)
            )
        if kind == "code":
            return f"```{block[2]}\n{block[1]}\n```"
        return "> " + block[1]

    def render(self) -> str:
        return "\n\n".join(self._render_block(block) for block in self.blocks)

    def block_count(self) -> int:
        return len(self.blocks)
