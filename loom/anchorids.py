"""Anchor ids: give each heading an explicit slug so links survive its wording changing.

A cross-reference to a heading usually points at the heading's
slug, computed from its text, which means editing the wording
of a heading silently breaks every link to it. Writing an
explicit anchor onto the heading fixes that: once a heading
carries a brace-hash id, links point at the id and the wording
can change freely. This adds those ids, appending the slug of
each heading's current text in the brace-hash form the common
renderers honour, as operations woven through the patch so a
heading keeps the strands it already had and only the anchor
is added. It computes the slug with the same rule the
cross-reference module reads by, so the anchor it writes is
exactly the target a link would have resolved to, and it skips
a heading that already carries an explicit id rather than
stacking a second, which makes the pass idempotent and safe to
run whenever headings are added. The slug is taken from the
heading text with any existing id stripped first, so a
re-run after a title edit does not fold a stale id into the
new slug. What it does not do is rewrite the links themselves;
it only ensures the targets exist and are stable, because the
links are the writer's to point where they mean, and a tool
that rewrote them would be guessing at intent the anchors do
not need to guess about.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.crossrefs import slugify
from loom.linewise import lines_of
from loom.patch import patch
from loom.weave import Op

HEADING = re.compile(r"^(#{1,6}\s+)(.*)$")
EXPLICIT_ID = re.compile(r"\s*\{#[a-z0-9-]+\}\s*$")


def _bare_title(rest: str) -> str:
    return EXPLICIT_ID.sub("", rest).rstrip()


def add_ids(author: Author) -> list[Op]:
    out = []
    for line in lines_of(author.weave):
        match = HEADING.match(line)
        if match is not None and not EXPLICIT_ID.search(match.group(2)):
            title = _bare_title(match.group(2))
            out.append(f"{match.group(1)}{title} {{#{slugify(title)}}}")
        else:
            out.append(line)
    return patch(author, "\n".join(out))


def has_id(heading_text: str) -> bool:
    return EXPLICIT_ID.search(heading_text) is not None
