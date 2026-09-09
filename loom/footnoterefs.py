"""Footnote refs: resolve Markdown's caret footnotes and number them by first use.

Markdown's footnote syntax is a caret reference in the prose,
a bracket-caret-label, and a matching definition line that
gives the note's text, and this reads both, matches them, and
numbers them the way footnotes are numbered, by the order they
are first referenced. It is distinct from the footnotes module,
which anchors notes to strand positions in the loom's own way;
this reads the textual Markdown form a document arrived
carrying or was written in. The numbering follows first
reference rather than definition order, because a reader
encounters the marks in reading order and expects one, two,
three down the page regardless of where the definitions sit,
and a footnote referenced twice keeps its first number both
times. The two failures a footnoted document grows are
surfaced: a reference with no definition, a mark that leads
nowhere, and a definition no reference points to, a note that
will never be seen. Telling a use from a definition is the one
parsing subtlety, and it is handled by the colon: a bracket-
caret-label followed by a colon is a definition, one not
followed by a colon is a reference, so a definition line's own
label is not miscounted as a reference to itself. Labels are
matched as written, not folded, because footnote labels are
often numbers or short tokens where case does not arise and
folding could merge two a writer meant to keep apart.
"""

from __future__ import annotations

import re

DEFINITION = re.compile(r"^\s*\[\^([^\]]+)\]:\s+(.*)$", re.MULTILINE)
USE = re.compile(r"\[\^([^\]]+)\](?!:)")


def definitions(text: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2).strip()
        for match in DEFINITION.finditer(text)
    }


def references(text: str) -> list[str]:
    return [match.group(1) for match in USE.finditer(text)]


def numbering(text: str) -> dict[str, int]:
    order: list[str] = []
    for label in references(text):
        if label not in order:
            order.append(label)
    return {label: number for number, label in enumerate(order, start=1)}


def undefined(text: str) -> list[str]:
    defined = definitions(text)
    return [label for label in references(text) if label not in defined]


def unused(text: str) -> list[str]:
    used = set(references(text))
    return sorted(
        label for label in definitions(text) if label not in used
    )


def report(text: str) -> str:
    refs = references(text)
    defs = definitions(text)
    if not refs and not defs:
        return "no footnotes; nothing to resolve"
    lines = [f"{len(set(refs))} footnote(s), {len(defs)} definition(s)"]
    missing = undefined(text)
    if missing:
        lines.append("  undefined: " + ", ".join(missing))
    idle = unused(text)
    if idle:
        lines.append("  unused definitions: " + ", ".join(idle))
    return "\n".join(lines)
