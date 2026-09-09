"""Reference links: resolve Markdown's label-and-definition links, and find the dangling ones.

Markdown lets a link name a label and define the url
elsewhere, keeping the prose clean: a use like the site in
brackets followed by the label home in brackets, and a
definition line giving home a url. This reads both and matches
them, so the two problems a reference-link document grows can
be surfaced: a use whose label was never defined, a link that
renders as plain bracket text and goes nowhere, and a
definition no use refers to, dead weight a writer meant to
reference and forgot. Labels are matched case-insensitively,
because Markdown folds a label's case, so Home and home are
one label and a document that defines one and uses the other
still links. The collapsed form, a use that gives a label and
an empty second bracket, resolves against its own text as the
label, the shorthand the format allows. The one form not
handled is named rather than silently mishandled: the shortcut
reference, a single bracketed label with no second bracket, is
indistinguishable from ordinary bracketed prose without
resolving every bracket against the definitions, and this does
not, because treating every bracketed word as a possible link
would flag half a document's asides as dangling references. So
it reads the unambiguous forms and reports what it finds,
leaving the shortcut form to a fuller parser that the feature
does not need to be.
"""

from __future__ import annotations

import re

DEFINITION = re.compile(r"^\s*\[([^\]]+)\]:\s+(\S+)", re.MULTILINE)
USE = re.compile(r"\[([^\]]+)\]\[([^\]]*)\]")


def definitions(text: str) -> dict[str, str]:
    return {
        match.group(1).lower(): match.group(2)
        for match in DEFINITION.finditer(text)
    }


def references(text: str) -> list[tuple[str, str]]:
    refs = []
    for match in USE.finditer(text):
        label = match.group(2) or match.group(1)
        refs.append((match.group(1), label.lower()))
    return refs


def undefined(text: str) -> list[str]:
    defined = definitions(text)
    return [
        label for _text, label in references(text) if label not in defined
    ]


def unused(text: str) -> list[str]:
    used = {label for _text, label in references(text)}
    return sorted(
        label for label in definitions(text) if label not in used
    )


def report(text: str) -> str:
    refs = references(text)
    defs = definitions(text)
    if not refs and not defs:
        return "no reference links; nothing to resolve"
    lines = [f"{len(refs)} reference(s), {len(defs)} definition(s)"]
    missing = undefined(text)
    if missing:
        lines.append("  undefined: " + ", ".join(missing))
    idle = unused(text)
    if idle:
        lines.append("  unused definitions: " + ", ".join(idle))
    return "\n".join(lines)
