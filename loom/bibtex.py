"""BibTeX: parse the common entry form into the citation module's sources.

Bibliographies arrive as BibTeX, and this reads the common
entry into a Source the citations module can hold: the entry
type and key, and the author, title, and year fields, whether
their values are wrapped in braces or quotes. It is a minimal
parser and says so plainly. It finds each entry by matching
the outer braces so an entry's own closing brace is not
mistaken for a field's, but it reads field values with a
simpler rule that does not descend into nested braces, so a
title written with an inner brace group, the trick BibTeX
users reach for to protect capitalization, is where this stops
being enough and a full parser earns its keep; that limit is
named rather than met with a half-correct guess. It reads the
three fields citations needs and ignores the rest, not because
the rest do not matter but because inventing storage for
fields the Source has nowhere to keep would be a promise the
citation model cannot honour. A year that is not a plain
number becomes no year rather than a parse error, since a
range or an in-press marker is a real value the numeric field
cannot hold, and losing the year is better than losing the
whole entry. What it produces plugs straight into a
Bibliography, so a BibTeX file becomes citations the rest of
the engine numbers and renders like any others.
"""

from __future__ import annotations

import re

from loom.citations import Bibliography, Source

FIELD = re.compile(r"(\w+)\s*=\s*(\{[^{}]*\}|\"[^\"]*\"|[^,]+)")


def _entries(text: str) -> list[tuple[str, str, str]]:
    found = []
    index = 0
    while True:
        at = text.find("@", index)
        if at < 0:
            break
        brace = text.find("{", at)
        if brace < 0:
            break
        depth = 0
        cursor = brace
        while cursor < len(text):
            if text[cursor] == "{":
                depth += 1
            elif text[cursor] == "}":
                depth -= 1
                if depth == 0:
                    break
            cursor += 1
        inner = text[brace + 1 : cursor]
        comma = inner.find(",")
        if comma >= 0:
            entry_type = text[at + 1 : brace].strip()
            key = inner[:comma].strip()
            found.append((entry_type, key, inner[comma + 1 :]))
        index = cursor + 1
    return found


def _fields(body: str) -> dict[str, str]:
    values = {}
    for match in FIELD.finditer(body):
        raw = match.group(2).strip()
        if raw and raw[0] in "{\"":
            raw = raw[1:-1]
        values[match.group(1).lower()] = raw.strip()
    return values


def parse(text: str) -> list[Source]:
    sources = []
    for _type, key, body in _entries(text):
        fields = _fields(body)
        year_text = fields.get("year", "")
        year = int(year_text) if year_text.isdigit() else None
        sources.append(
            Source(
                key=key,
                author=fields.get("author", ""),
                title=fields.get("title", ""),
                year=year,
            )
        )
    return sources


def into_bibliography(text: str) -> Bibliography:
    biblio = Bibliography()
    for source in parse(text):
        biblio.enter(source)
    return biblio
