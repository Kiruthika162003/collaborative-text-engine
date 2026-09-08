"""Markdown import: plain markup parsed into a woven fabric with its marks.

Text arrives from outside the loom carrying formatting in
Markdown's stars, and this brings it in whole: the visible
characters become a woven run typed by a named importer,
and the bold and italic spans the stars delimited become
real marks pinned to the strands underneath, so an imported
document is indistinguishable from one typed in the room,
which is the only import worth having. Parsing is the
careful half. The stars are stripped from the text but
their spans are remembered by character offset into the
clean text, then translated to strand ids after weaving,
because a mark cannot pin to a strand that does not exist
yet, and doing it in the wrong order is the bug that makes
imported bold land one character off. Unmatched stars are
left as literal text rather than guessed into a span,
because a lone star is a multiplication sign or a typo far
more often than a formatting error, and inventing a span
around it corrupts the very text the import was meant to
preserve. The importer's site names every strand, so the
byline of an imported document honestly reads as imported,
not as written by whoever pressed the button.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.author import Author
from loom.ids import OpId
from loom.marks import Mark, Wardrobe


@dataclass
class ParsedMarkdown:
    text: str
    spans: list  # (style, start, end) offsets into text


def _tokenize(source: str) -> list:
    tokens: list = []
    i = 0
    n = len(source)
    while i < n:
        if source[i] == "*":
            run = 1
            while i + run < n and source[i + run] == "*":
                run += 1
            if run >= 2:
                tokens.append(("marker", "bold", "**"))
                i += 2
            else:
                tokens.append(
                    ("marker", "italic", "*")
                )
                i += 1
            continue
        tokens.append(("text", source[i], source[i]))
        i += 1
    return tokens


def parse(source: str) -> ParsedMarkdown:
    tokens = _tokenize(source)
    paired: set = set()
    open_by_style: dict = {}
    for index, (kind, style, _raw) in enumerate(tokens):
        if kind != "marker":
            continue
        if style in open_by_style:
            paired.add(open_by_style.pop(style))
            paired.add(index)
        else:
            open_by_style[style] = index

    out: list[str] = []
    spans: list = []
    span_open: dict = {}
    for index, (kind, style, raw) in enumerate(tokens):
        if kind == "text":
            out.append(raw)
            continue
        if index not in paired:
            out.extend(raw)
            continue
        if style in span_open:
            start = span_open.pop(style)
            spans.append((style, start, len(out)))
        else:
            span_open[style] = len(out)
    return ParsedMarkdown(
        text="".join(out), spans=spans
    )


def load(
    source: str, importer: str = "import"
) -> tuple[Author, Wardrobe]:
    parsed = parse(source)
    author = Author(site=importer)
    ops = (
        author.type_at(0, parsed.text)
        if parsed.text
        else []
    )
    wardrobe = Wardrobe(weave=author.weave)
    counter = 1000
    for style, start, end in parsed.spans:
        if end <= start:
            continue
        wardrobe.dress(
            Mark(
                id=OpId(site=importer, counter=counter),
                style=style,
                start=ops[start].id,
                end=ops[end - 1].id,
            )
        )
        counter += 1
    return author, wardrobe
