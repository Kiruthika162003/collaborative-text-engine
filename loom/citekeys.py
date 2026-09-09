"""Cite keys: generate a citation key from a source, disambiguating the collisions.

A citation key is the short handle a document refers to a
source by, and the common scheme is the first author's surname
followed by the year, smith2020, which this generates from a
source's author and year fields. The surname is the part
before the first comma when the author is written surname-first,
the convention the field holds, or the first word otherwise,
lowercased and stripped to letters and digits so the key is a
safe token; the year is the four digits or nd when the source
has none, the standard mark for no date. The interesting part
is collisions: two sources by the same author in the same year
produce the same base key, and a bibliography cannot have two
of one key, so this disambiguates them the way citation styles
do, appending a, b, c in the order the sources are given, and
it only appends when there is actually a collision, so a lone
smith2020 stays smith2020 and does not become smith2020a for
no reason. The disambiguation order is the input order, which
is deterministic and stated, so the same list of sources
always assigns the same keys; a caller who wants a particular
source to be the unsuffixed a orders it first. An author field
with neither a comma nor a word falls back to anon, because a
source can arrive without an author and a key of just a year
collides with every other yearless source, where anon at least
groups them under a name.
"""

from __future__ import annotations

import re
from collections import Counter

from loom.citations import Source


def make_key(source: Source) -> str:
    author = source.author.strip()
    if "," in author:
        surname = author.split(",", 1)[0]
    elif author.split():
        surname = author.split()[0]
    else:
        surname = "anon"
    surname = re.sub(r"[^a-z0-9]", "", surname.lower()) or "anon"
    year = str(source.year) if source.year is not None else "nd"
    return f"{surname}{year}"


def assign_keys(sources: list[Source]) -> list[tuple[Source, str]]:
    base_counts = Counter(make_key(source) for source in sources)
    used: Counter = Counter()
    result = []
    for source in sources:
        base = make_key(source)
        if base_counts[base] > 1:
            suffix = chr(ord("a") + used[base])
            used[base] += 1
            result.append((source, base + suffix))
        else:
            result.append((source, base))
    return result
