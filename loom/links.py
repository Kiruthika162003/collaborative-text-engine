"""Links: URLs and emails found in the cloth and pinned so they survive edits.

Writers type urls and addresses and expect them to become
clickable, and this module finds them, but the finding is
the easy half; the hard half is that a link found at
character forty is at character forty-three by the time
anyone clicks it, so each detected link pins to the strands
of its first and last character and reports its current
position on demand. Detection runs on the visible cloth
with patterns deliberately conservative, a url needs a
scheme and an email needs the shape everyone agrees on,
because a link detector that is too eager turns every
sentence with a dot into a minefield of false clicks. A
link whose text is edited becomes stale, the same honest
staleness a comment or a bookmark reports, because a link
that silently re-scans and re-points is offering to
navigate somewhere the writer never typed. The catalogue
separates urls from emails because they open different
doors, and counts them because a document that is mostly
links is a bibliography wearing an essay's clothes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave

URL = re.compile(r"https?://[^\s]+")
EMAIL = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


@dataclass(frozen=True)
class Link:
    kind: str
    text: str
    first: OpId
    last: OpId
    found_at: int


def _visible(weave: Weave):
    return [
        strand
        for strand in weave.strands
        if not strand.sheared
    ]


def detect(weave: Weave) -> list[Link]:
    visible = _visible(weave)
    cloth = "".join(s.glyph for s in visible)
    found: list[Link] = []
    for kind, pattern in (
        ("url", URL),
        ("email", EMAIL),
    ):
        for match in pattern.finditer(cloth):
            start, end = match.start(), match.end() - 1
            found.append(
                Link(
                    kind=kind,
                    text=match.group(),
                    first=visible[start].id,
                    last=visible[end].id,
                    found_at=start,
                )
            )
    found.sort(key=lambda link: link.found_at)
    return found


def still_valid(
    weave: Weave, link: Link
) -> bool:
    first = weave.by_id.get(link.first)
    last = weave.by_id.get(link.last)
    if first is None or last is None:
        return False
    stretch = "".join(
        strand.glyph
        for strand in weave.strands[first : last + 1]
        if not strand.sheared
    )
    return stretch == link.text


def catalogue(weave: Weave) -> str:
    found = detect(weave)
    if not found:
        return "no links; the cloth is all prose"
    urls = [link for link in found if link.kind == "url"]
    emails = [
        link for link in found if link.kind == "email"
    ]
    lines = [
        f"{len(urls)} url(s), {len(emails)} email(s):"
    ]
    for link in found:
        lines.append(f"  {link.kind}: {link.text}")
    return "\n".join(lines)
