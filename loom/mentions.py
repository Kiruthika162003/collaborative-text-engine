"""Mentions: at-signs in the prose resolved against who is actually in the room.

A mention is an at-sign followed by a handle, the way every
chat and comment thread writes one, and this reads them off
the visible cloth and checks each against the roster of
people actually collaborating. The check is the point: an
at-sign is a promise that a named person will be notified,
and a mention of someone not in the room is a promise made
to nobody, almost always a typo in a name, so those are
gathered separately as the probable mistakes they are
rather than counted among the real mentions. Each mention
pins to the strand of its at-sign, so a list of who was
mentioned survives the surrounding text being edited, the
pin discipline every anchor here shares, and a mention
whose at-sign is later deleted simply stops being found
because it is no longer in the text. The handle grammar is
the same one site names obey, a lowercase letter then
letters, digits, and dashes, so a stray at-sign in an email
address or a decorative flourish is not mistaken for a
mention of a person, and an at-sign with nothing after it
is not a mention of the empty name.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave

MENTION = re.compile(r"@([a-z][a-z0-9-]*)")


@dataclass(frozen=True)
class Mention:
    handle: str
    pin: OpId
    known: bool


def _visible_ids(weave: Weave) -> list[OpId]:
    return [
        strand.id for strand in weave.strands if not strand.sheared
    ]


def mentions(weave: Weave, roster: set[str]) -> list[Mention]:
    text = weave.text()
    ids = _visible_ids(weave)
    found = []
    for match in MENTION.finditer(text):
        handle = match.group(1)
        found.append(
            Mention(
                handle=handle,
                pin=ids[match.start()],
                known=handle in roster,
            )
        )
    return found


def mentioned(weave: Weave, roster: set[str]) -> set[str]:
    return {
        mention.handle
        for mention in mentions(weave, roster)
        if mention.known
    }


def unknown(weave: Weave, roster: set[str]) -> list[Mention]:
    return [
        mention
        for mention in mentions(weave, roster)
        if not mention.known
    ]


def page(weave: Weave, roster: set[str]) -> str:
    found = mentions(weave, roster)
    if not found:
        return "no mentions; nobody was named"
    real = sorted(mentioned(weave, roster))
    strangers = sorted({m.handle for m in unknown(weave, roster)})
    lines = [f"{len(found)} mention(s):"]
    if real:
        lines.append("  in the room: " + ", ".join(real))
    if strangers:
        lines.append(
            "  not in the room (probable typos): "
            + ", ".join(strangers)
        )
    return "\n".join(lines)
