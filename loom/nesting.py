"""Nesting: promote and demote headings by editing their hash marks.

A heading's level is not a property to toggle; it is the
count of hash marks at the head of its line, so changing a
level is editing text, shearing a hash to promote a section
one step shallower or inserting one to demote it deeper. The
headings module already pins each heading to its first hash,
and this rides that pin: promote shears the pinned hash and
the heading's new first hash becomes the pin next time the
outline is read, demote inserts a hash before it and the new
one takes the pin, both recomputed rather than stored. A
section rarely moves alone, so the subtree operations shift
a heading together with every heading nested under it, the
contiguous run of deeper headings that follow, which is what
a writer means by promote this section: the children come
with it or the outline tears. The pins of the whole run are
resolved before any hash is touched and each heading's live
position is recomputed as it is reached, the same guard the
case and replace operations keep, so an insert that shifts
the glyphs below it does not send a later heading's edit to
the wrong line. Promoting a top-level heading is refused
because there is no level zero, and demoting a level-six
heading is refused because Markdown stops at six, and a
subtree operation refuses whole rather than half-applying
when any member would cross those edges, since half a
promotion is a broken outline nobody asked for.
"""

from __future__ import annotations

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.headings import Heading, headings
from loom.ids import OpId
from loom.weave import Op, Weave

MAX_LEVEL = 6


def _heading_at(weave: Weave, pin: OpId) -> Heading:
    for heading in headings(weave):
        if heading.pin == pin:
            return heading
    raise Missing(
        f"{pin.wire()} does not head a section; nesting "
        "edits a heading, not a line of prose"
    )


def _visible_of(weave: Weave, pin: OpId) -> int:
    position = weave.by_id[pin]
    return sum(
        1 for strand in weave.strands[:position] if not strand.sheared
    )


def level_at(weave: Weave, pin: OpId) -> int:
    return _heading_at(weave, pin).level


def _subtree(weave: Weave, pin: OpId) -> list[Heading]:
    found = headings(weave)
    index = next(
        (i for i, heading in enumerate(found) if heading.pin == pin),
        None,
    )
    if index is None:
        raise Missing(
            f"{pin.wire()} does not head a section"
        )
    target = found[index]
    run = [target]
    for heading in found[index + 1 :]:
        if heading.level <= target.level:
            break
        run.append(heading)
    return run


def promote(author: Author, pin: OpId) -> list[Op]:
    heading = _heading_at(author.weave, pin)
    if heading.level <= 1:
        raise Invalid(
            "a top-level heading cannot promote; there is "
            "no level zero"
        )
    return author.erase_at(_visible_of(author.weave, pin), 1)


def demote(author: Author, pin: OpId) -> list[Op]:
    heading = _heading_at(author.weave, pin)
    if heading.level >= MAX_LEVEL:
        raise Invalid(
            "a level-six heading cannot demote; Markdown "
            "stops at six"
        )
    return author.type_at(_visible_of(author.weave, pin), "#")


def promote_subtree(author: Author, pin: OpId) -> list[Op]:
    members = _subtree(author.weave, pin)
    if any(heading.level <= 1 for heading in members):
        raise Invalid(
            "a member is already top-level; promoting the "
            "subtree would ask for level zero"
        )
    pins = [heading.pin for heading in members]
    ops: list[Op] = []
    for member_pin in pins:
        ops.extend(
            author.erase_at(_visible_of(author.weave, member_pin), 1)
        )
    return ops


def demote_subtree(author: Author, pin: OpId) -> list[Op]:
    members = _subtree(author.weave, pin)
    if any(heading.level >= MAX_LEVEL for heading in members):
        raise Invalid(
            "a member is already at level six; demoting the "
            "subtree would cross Markdown's floor"
        )
    pins = [heading.pin for heading in members]
    ops: list[Op] = []
    for member_pin in pins:
        ops.extend(
            author.type_at(_visible_of(author.weave, member_pin), "#")
        )
    return ops
