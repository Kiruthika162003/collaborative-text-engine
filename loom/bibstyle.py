"""Bibliography style: render a source list alphabetically and cite it author-year.

The citations module numbers references by where they first
appear, which is one house style; this offers the other, the
alphabetical reference list and the author-year in-text
citation that the sciences and humanities mostly use. The
alphabetical list sorts the bibliography's sources by author
and renders each as a reference line, so a works-cited page
reads in the order a reader scans for a name, and the
author-year form renders a single source as the parenthetical
a sentence carries, Smith comma year. The sort keys on the
author field exactly as it was entered, which assumes the
surname-first convention the field is meant to hold, and says
so: a source entered given-name-first will sort under the
given name, which is the field's problem to fix, not a
guess this module should make by parsing names it cannot
reliably split. A source with no author sorts under its
title, because a titled anonymous work still has a place in
the alphabet, and a source with no year cites as n.d., the
standard mark for no date, rather than an empty parenthesis
that looks like a bug. None of this changes the bibliography;
it reads it and formats it, so the same source list can be
rendered numeric by the citations module and alphabetical
here without either owning the data.
"""

from __future__ import annotations

from loom.citations import Bibliography, Source


def author_year(source: Source) -> str:
    who = source.author.strip() or "Anon"
    year = source.year if source.year is not None else "n.d."
    return f"({who}, {year})"


def _sort_key(source: Source) -> tuple[str, int]:
    name = source.author.strip().lower() or source.title.strip().lower()
    return (name, source.year if source.year is not None else 0)


def alphabetical(biblio: Bibliography) -> list[str]:
    ordered = sorted(biblio.sources.values(), key=_sort_key)
    return [source.reference() for source in ordered]


def bibliography(biblio: Bibliography) -> str:
    lines = alphabetical(biblio)
    if not lines:
        return "an empty bibliography lists nothing"
    return "\n".join(lines)


def in_text(biblio: Bibliography, key: str) -> str:
    source = biblio.sources.get(key)
    if source is None:
        return f"[unknown source {key!r}]"
    return author_year(source)
