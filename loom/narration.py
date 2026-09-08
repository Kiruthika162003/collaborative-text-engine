"""Narration: the document said aloud, formatting announced not shown.

A screen reader cannot see bold; it must be told, and
narration renders the dressed fabric into a stream a reader
speaks, announcing each formatted span with words rather
than symbols, bold start and bold end around the emphasized
run, so a listener knows where the emphasis begins and ends
rather than hearing a flat sentence that lost its stress.
Headings are announced by level, heading level two, because
a listener navigating by structure needs the level spoken,
and list items are announced as items so the ear can count
them. The narration reads the wardrobe's spans and the
heading and list organs rather than re-deriving any of it,
because those computations are settled elsewhere and a
second copy would drift. Plain unformatted prose narrates
as itself with no announcements, because a reader who
hears bold start before every sentence stops hearing it,
and the announcement is only useful where the formatting
actually is.
"""

from __future__ import annotations

from loom.headings import headings
from loom.lists import items
from loom.marks import Wardrobe


def narrate(wardrobe: Wardrobe) -> str:
    parts: list[str] = []
    for text, styles in wardrobe.spans():
        opened = sorted(styles)
        for style in opened:
            parts.append(f"[{style} start] ")
        parts.append(text)
        for style in reversed(opened):
            parts.append(f" [{style} end]")
    return "".join(parts)


def structure(wardrobe: Wardrobe) -> str:
    weave = wardrobe.weave
    lines = []
    for heading in headings(weave):
        lines.append(
            f"(heading level {heading.level}) "
            f"{heading.title}"
        )
    for item in items(weave):
        lines.append(f"(item) {item.text}")
    if not lines:
        return "flat prose; nothing to announce"
    return "\n".join(lines)


def announcements(wardrobe: Wardrobe) -> int:
    count = 0
    for _text, styles in wardrobe.spans():
        count += len(styles) * 2
    return count


def plain_line(wardrobe: Wardrobe) -> str:
    return wardrobe.weave.text()
