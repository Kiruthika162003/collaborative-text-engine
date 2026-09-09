"""Cross-references: the internal links between sections, resolved against the headings.

Where the links module finds the urls that leave the
document, this finds the links that stay inside it, the
Markdown anchor links and the double-bracket wiki links that
point one section at another, and checks each against the
headings it could land on. The check is the value: a link to
a section that does not exist is a broken promise a reader
follows into nothing, so those are gathered as broken with
the target named, and a heading nothing links to is an
orphan, reachable only by scrolling, which a writer building
a navigable document wants to know about. Targets are
matched by slug, the heading title lowercased with spaces
turned to hyphens and punctuation dropped, the convention
the common tools already use, and when two headings slug to
the same anchor the target is ambiguous and flagged rather
than silently resolved to the first, because a link that
lands on one of two identically named sections lands on the
wrong one half the time. The slug rule is a convention, not
a law, and it is named as such: a document whose tool slugs
differently will disagree at the edges, and this says which
rule it followed rather than presenting its slugs as the
only ones possible.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.headings import headings
from loom.weave import Weave

MD_LINK = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
WIKI_LINK = re.compile(r"\[\[([^\]]+)\]\]")


def slugify(title: str) -> str:
    lowered = title.strip().lower()
    hyphenated = re.sub(r"\s+", "-", lowered)
    cleaned = re.sub(r"[^a-z0-9-]", "", hyphenated)
    return re.sub(r"-+", "-", cleaned).strip("-")


@dataclass(frozen=True)
class Ref:
    label: str
    target: str
    resolved: bool


def _heading_slugs(weave: Weave) -> dict[str, int]:
    counts: dict[str, int] = {}
    for heading in headings(weave):
        slug = slugify(heading.title)
        counts[slug] = counts.get(slug, 0) + 1
    return counts


def crossrefs(weave: Weave) -> list[Ref]:
    text = weave.text()
    slugs = _heading_slugs(weave)
    refs = []
    for match in MD_LINK.finditer(text):
        target = match.group(2).strip()
        refs.append(
            Ref(
                label=match.group(1),
                target=target,
                resolved=target in slugs,
            )
        )
    for match in WIKI_LINK.finditer(text):
        target = slugify(match.group(1))
        refs.append(
            Ref(
                label=match.group(1),
                target=target,
                resolved=target in slugs,
            )
        )
    return refs


def broken(weave: Weave) -> list[Ref]:
    return [ref for ref in crossrefs(weave) if not ref.resolved]


def ambiguous(weave: Weave) -> list[str]:
    return sorted(
        slug
        for slug, count in _heading_slugs(weave).items()
        if count > 1
    )


def orphans(weave: Weave) -> list[str]:
    linked = {ref.target for ref in crossrefs(weave) if ref.resolved}
    return sorted(
        slug for slug in _heading_slugs(weave) if slug not in linked
    )


def report(weave: Weave) -> str:
    refs = crossrefs(weave)
    if not refs and not _heading_slugs(weave):
        return "no headings and no links; nothing to cross-reference"
    lines = [
        f"{len(refs)} internal link(s), "
        f"{len(broken(weave))} broken"
    ]
    hanging = orphans(weave)
    if hanging:
        lines.append("  orphan sections: " + ", ".join(hanging))
    tangled = ambiguous(weave)
    if tangled:
        lines.append("  ambiguous slugs: " + ", ".join(tangled))
    return "\n".join(lines)
