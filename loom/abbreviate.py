"""Abbreviate: expand defined abbreviations in place, matching whole words only.

Writers type btw and e.g. and a house set of shorthands, and
this expands them from a caller's glossary of abbreviation to
expansion, replacing each as operations woven through the
patch so only the abbreviations change. The match is whole-
word and case-insensitive, which is the pair of rules that
keeps it from doing harm: whole-word so btw inside a longer
word is not torn open, and case-insensitive so BTW at the
start of a sentence expands like btw mid-sentence. When one
abbreviation is a prefix of another the longer is tried first,
so a glossary with both eg and e expands eg to its own
meaning rather than expanding the leading e and stranding a g.
The expansion is inserted verbatim, the glossary's value as
written, with no attempt to match the sentence case of the
abbreviation it replaced, which is stated because a caller who
wants a capitalized expansion at a sentence start should
define it that way rather than expect the tool to guess when
to capitalize. It converges across replicas because it patches,
and a document with none of the glossary's abbreviations mints
nothing, so it is safe to run on a document that has already
been expanded or never needed it.
"""

from __future__ import annotations

import re

from loom.author import Author
from loom.patch import patch
from loom.weave import Op


def expand(text: str, glossary: dict[str, str]) -> str:
    for abbreviation in sorted(glossary, key=len, reverse=True):
        pattern = re.compile(
            r"\b" + re.escape(abbreviation) + r"\b", re.IGNORECASE
        )
        expansion = glossary[abbreviation]
        text = pattern.sub(lambda _match, value=expansion: value, text)
    return text


def expand_ops(author: Author, glossary: dict[str, str]) -> list[Op]:
    return patch(author, expand(author.text(), glossary))


def would_expand(text: str, glossary: dict[str, str]) -> bool:
    return expand(text, glossary) != text
