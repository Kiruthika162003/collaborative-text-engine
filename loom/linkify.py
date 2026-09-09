"""Linkify: wrap the bare URLs a writer typed in autolink brackets, as real operations.

The links module finds urls; this turns the bare ones into
autolinks, wrapping each in the angle brackets that make it a
link a renderer will honour, and it does so as operations
every replica weaves, so the document itself carries the
links rather than one screen guessing where they are. The
care is in what it leaves alone. A url already wrapped in
angle brackets is skipped, and so is one already serving as a
markdown link's target, because wrapping either again would
double the brackets and break the link the writer already
made, and the check for both is the single character before
the url, an angle bracket or an open parenthesis. Trailing
sentence punctuation is trimmed out of the link, so a url at
the end of a sentence links to the address and not to the
address plus the full stop, which is the difference between a
link that works and one that four-oh-fours on the period. The
url pattern is the conservative one the links module keeps, a
scheme required, because a linkifier too eager to see a url in
every dotted token turns a document into a field of false
links, and the operations are minted from the rightmost url
back so the insertions do not shift the positions of the urls
still waiting to be wrapped.
"""

from __future__ import annotations

from loom.author import Author
from loom.links import URL
from loom.weave import Op

TRAILING = ".,;:!?"


def bare_url_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for match in URL.finditer(text):
        start = match.start()
        end = match.end()
        while end > start and text[end - 1] in TRAILING:
            end -= 1
        before = text[start - 1] if start > 0 else ""
        if before in {"<", "("}:
            continue
        spans.append((start, end))
    return spans


def autolink(author: Author) -> list[Op]:
    text = author.text()
    ops: list[Op] = []
    for start, end in sorted(bare_url_spans(text), reverse=True):
        ops.extend(author.type_at(end, ">"))
        ops.extend(author.type_at(start, "<"))
    return ops


def would_link(text: str) -> int:
    return len(bare_url_spans(text))
