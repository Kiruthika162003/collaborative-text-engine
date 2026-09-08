"""Pages: the cloth cut into numbered pages, the numbers being weather too.

A page number is a line number wearing a different hat: it
is a position, computed from where the text sits now, and
it moves the instant someone types above it, so this module
computes pages fresh from the living cloth rather than
storing a page a paragraph believes it lives on. Pages are
line runs, a fixed count of visible lines each, the last
page taking whatever is left, and every page carries the
strand id of its first line's first glyph so a reader who
says take me to page three lands on the strand that opened
page three when the pagination was drawn, which may sit on
page two by the time they arrive if lines were cut above
it, and that is honest rather than broken: the pin is a
place, the page number was a snapshot. An empty line opens
a page with no pin, because there is no glyph to point at,
and a page count on an empty document is one, not zero,
since a blank page is still a page a reader can turn to.
The line budget must be positive, a page of zero lines
being a request that cannot be honoured, and it is refused
at the door rather than looping forever trying to fill
pages that can hold nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Invalid, Missing
from loom.ids import OpId
from loom.linewise import line_of, lines_of, visible_index
from loom.weave import Weave


@dataclass(frozen=True)
class Page:
    number: int
    start_line: int
    lines: list[str]
    start_pin: OpId | None


def _guard(lines_per_page: int) -> None:
    if lines_per_page <= 0:
        raise Invalid(
            "a page of zero lines cannot be filled; the "
            "budget must be positive"
        )


def _pin_of_line(weave: Weave, line: int, text: str) -> OpId | None:
    if not text:
        return None
    index = visible_index(weave, line, 0)
    return weave.strand_at_visible(index).id


def paginate(weave: Weave, lines_per_page: int) -> list[Page]:
    _guard(lines_per_page)
    held = lines_of(weave)
    pages = []
    for number, start in enumerate(
        range(0, len(held), lines_per_page), start=1
    ):
        chunk = held[start : start + lines_per_page]
        pages.append(
            Page(
                number=number,
                start_line=start,
                lines=chunk,
                start_pin=_pin_of_line(weave, start, chunk[0]),
            )
        )
    return pages


def page_count(weave: Weave, lines_per_page: int) -> int:
    _guard(lines_per_page)
    held = lines_of(weave)
    return (len(held) + lines_per_page - 1) // lines_per_page


def page_of_line(weave: Weave, line: int, lines_per_page: int) -> int:
    _guard(lines_per_page)
    held = lines_of(weave)
    if not 0 <= line < len(held):
        raise Missing(
            f"line {line} of a {len(held)}-line cloth"
        )
    return line // lines_per_page + 1


def page_of_strand(
    weave: Weave, strand_id: OpId, lines_per_page: int
) -> int:
    line = line_of(weave, strand_id)
    return page_of_line(weave, line, lines_per_page)


def render(weave: Weave, lines_per_page: int) -> str:
    pages = paginate(weave, lines_per_page)
    total = len(pages)
    blocks = []
    for page in pages:
        body = "\n".join(page.lines)
        blocks.append(f"[page {page.number} of {total}]\n{body}")
    return "\n\n".join(blocks)
