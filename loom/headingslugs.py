"""Heading slugs: a unique anchor per heading, duplicates disambiguated the common way.

A slug computed from a heading's text is not unique when two
headings share a title, and a table of contents that linked
both to one anchor would send every click to the first. This
generates a unique slug per heading, computing the base slug
the cross-reference module's way and disambiguating a repeat
by appending a counter, the scheme the common tools use: the
first Intro is intro, the second intro-1, the third intro-2,
numbered in document order so the mapping is deterministic and
a link generated once stays valid. It reports the collisions
too, the base slugs that more than one heading produced, which
is the thing a writer wants to know because a disambiguated
slug is stable but ugly and often the real fix is to make the
headings distinct. The disambiguation is by order, which means
inserting a second heading with an existing title renumbers
the ones after it, the same positional truth every numbered
thing in this codebase carries; a slug is a position's name,
and positions move. A heading whose text slugs to nothing, all
punctuation with no letters or digits, gets the empty base and
its disambiguated forms, which is stated rather than special-
cased, because inventing a name for a heading that has none
would be guessing at text the writer did not provide.
"""

from __future__ import annotations

from loom.crossrefs import slugify
from loom.headings import headings
from loom.weave import Weave


def unique_slugs(weave: Weave) -> list[tuple[str, str]]:
    seen: dict[str, int] = {}
    result = []
    for heading in headings(weave):
        base = slugify(heading.title)
        if base in seen:
            seen[base] += 1
            slug = f"{base}-{seen[base]}"
        else:
            seen[base] = 0
            slug = base
        result.append((heading.title, slug))
    return result


def slug_for(weave: Weave, index: int) -> str:
    return unique_slugs(weave)[index][1]


def collisions(weave: Weave) -> list[str]:
    counts: dict[str, int] = {}
    for heading in headings(weave):
        base = slugify(heading.title)
        counts[base] = counts.get(base, 0) + 1
    return sorted(base for base, count in counts.items() if count > 1)
