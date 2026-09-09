"""Acronyms: the all-caps initialisms found, matched to their definitions or flagged.

Technical documents are dense with acronyms, and the courtesy
a good one keeps is defining each on first use, so this finds
the all-caps tokens and checks whether the document ever
spells them out. A definition is caught two ways, the acronym
followed by its expansion in parentheses and the expansion
followed by the acronym in parentheses, the two shapes a
writer actually types, and an acronym that appears without
either anywhere in the document is reported as undefined, the
courtesy the writer forgot. The detection is a heuristic and
says so: a run of two or more capital letters is treated as
an acronym, which catches HTTP and API and also catches a
word a writer SHOUTED for emphasis and a Roman numeral like
III, false positives that a dictionary would filter but this
does not, because the alternative is a curated list that goes
stale and a document with a novel acronym the list never
heard of. The honest move is to report what the rule found
and name the rule, so a reader who sees NASA flagged as
undefined understands it as the rule working exactly as
described rather than a claim that NASA is not a real
acronym. Single capitals are not acronyms, because I and A
are words, and the sentence-initial capital of an ordinary
word never trips the rule since it takes two.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from loom.weave import Weave

ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]+\b")
DEFINE_AFTER = re.compile(r"\b([A-Z][A-Z0-9]+)\s*\(([^)]+)\)")
DEFINE_BEFORE = re.compile(
    r"((?:[A-Z][A-Za-z0-9]*\s+){1,6})\(([A-Z][A-Z0-9]+)\)"
)


@dataclass(frozen=True)
class Acronym:
    token: str
    position: int


def acronyms(weave: Weave) -> list[Acronym]:
    text = weave.text()
    seen: dict[str, int] = {}
    for match in ACRONYM.finditer(text):
        token = match.group(0)
        if token not in seen:
            seen[token] = match.start()
    return [
        Acronym(token=token, position=start)
        for token, start in seen.items()
    ]


def definitions(weave: Weave) -> dict[str, str]:
    text = weave.text()
    found: dict[str, str] = {}
    for match in DEFINE_AFTER.finditer(text):
        found.setdefault(match.group(1), match.group(2).strip())
    for match in DEFINE_BEFORE.finditer(text):
        found.setdefault(match.group(2), match.group(1).strip())
    return found


def undefined(weave: Weave) -> list[str]:
    defined = definitions(weave)
    return sorted(
        acronym.token
        for acronym in acronyms(weave)
        if acronym.token not in defined
    )


def report(weave: Weave) -> str:
    found = acronyms(weave)
    if not found:
        return "no acronyms; the document spells everything out"
    defined = definitions(weave)
    lines = [
        f"{len(found)} acronym(s), {len(defined)} defined:"
    ]
    missing = undefined(weave)
    if missing:
        lines.append("  undefined: " + ", ".join(missing))
    return "\n".join(lines)
