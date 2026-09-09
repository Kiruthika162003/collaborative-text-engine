"""Mail merge: fill double-brace placeholders from a data map or the front matter.

A template carries placeholders, a field name in double
braces, and merging replaces each with its value, the way a
form letter or a generated report is built. This fills them as
operations woven through the patch, so only the placeholders
change and the surrounding text keeps its strands, and it can
draw the values from a caller's map or from the document's own
front matter, which lets a document carry its own fill values
at the top and expand them into the body. The decision that
earns its keep is what to do with a placeholder the data does
not supply: it is left standing, braces and all, rather than
replaced with an empty string. A blank where a name should be
is a silent error a reader might miss and a template author
certainly wants to catch, so the unfilled placeholder stays
visible and is reported by name, turning a missing value into
a thing seen rather than a gap guessed past. The placeholder
grammar is the common double-brace form with a word-character
name, deliberately narrow so a stray brace in prose is not
mistaken for a field, and filling is idempotent on the
placeholders it cannot fill: run it again with the same data
and the same ones remain, because there is nothing new to
substitute, which is the honest behaviour for a merge waiting
on values it does not yet have.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.frontmatter import parse
from loom.patch import patch
from loom.weave import Op

FIELD = re.compile(r"\{\{(\w+)\}\}")


def fill(text: str, data: dict[str, str]) -> str:
    return FIELD.sub(
        lambda match: str(data.get(match.group(1), match.group(0))), text
    )


def fields(text: str) -> list[str]:
    seen: list[str] = []
    for match in FIELD.finditer(text):
        if match.group(1) not in seen:
            seen.append(match.group(1))
    return seen


def unfilled(text: str, data: dict[str, str]) -> list[str]:
    return [name for name in fields(text) if name not in data]


def merge(author: Author, data: dict[str, str]) -> list[Op]:
    return patch(author, fill(author.text(), data))


def merge_from_frontmatter(author: Author) -> list[Op]:
    return merge(author, parse(author.weave).fields)
