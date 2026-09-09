"""Hashtags: the topic tags in the prose, counted and pinned.

A hashtag marks a topic the way a mention marks a person, and
this reads them off the visible cloth, folds them to one case
so Draft and draft are one tag, and counts how often each
appears, because the value of tags over mentions is the tally:
the tags a document returns to are the topics it is actually
about, and the count surfaces them. The grammar requires a
letter right after the hash, so a heading's hash followed by a
space is not a tag and neither is a bare number, which keeps
an issue reference like the hash one two three from being
read as a topic it never was. Each tag pins to the strand of
its hash, so a list of a document's topics survives edits
above them, and a tag whose hash is deleted stops being
found, the honest staleness every anchor here reports. The
cloud renders the tags in descending frequency, which is the
order a reader scanning for what matters wants, ties broken
alphabetically so the same document always renders the same
cloud, and a document with no tags says so plainly rather
than printing an empty cloud that implies the writer forgot
to tag rather than chose not to.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave

TAG = re.compile(r"#([A-Za-z][A-Za-z0-9_-]*)")


@dataclass(frozen=True)
class Tag:
    name: str
    pin: OpId
    position: int


def _visible_ids(weave: Weave) -> list[OpId]:
    return [
        strand.id for strand in weave.strands if not strand.sheared
    ]


def tags(weave: Weave) -> list[Tag]:
    text = weave.text()
    ids = _visible_ids(weave)
    found = []
    for match in TAG.finditer(text):
        found.append(
            Tag(
                name=match.group(1).lower(),
                pin=ids[match.start()],
                position=match.start(),
            )
        )
    return found


def unique_tags(weave: Weave) -> set[str]:
    return {tag.name for tag in tags(weave)}


def tag_counts(weave: Weave) -> dict[str, int]:
    counts: dict[str, int] = {}
    for tag in tags(weave):
        counts[tag.name] = counts.get(tag.name, 0) + 1
    return counts


def most_used(weave: Weave) -> str | None:
    counts = tag_counts(weave)
    if not counts:
        return None
    return max(counts, key=lambda name: (counts[name], name))


def cloud(weave: Weave) -> str:
    counts = tag_counts(weave)
    if not counts:
        return "no tags; the document names no topics"
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return "\n".join(f"#{name} ({count})" for name, count in ranked)
