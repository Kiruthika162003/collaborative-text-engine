"""Tokens: text split into typed pieces, every character accounted for.

Many tools here ask the same first question, where are the
words, and each answers it slightly differently; this is the
one place that answer is made once and made exhaustive. It
splits text into four kinds of token, word, number, space,
and symbol, and the tokens tile the text with no gaps, so the
sum of their lengths is the length of the input and no
character falls through. The boundary choices are decisions,
not facts, and they are named: a contraction like don't is one
word because its apostrophe binds, a decimal like three point
one four is one number because its dot binds, and a
hyphenated pair is two words with a symbol between because the
hyphen in plain text is as often a dash as a joiner and
guessing wrong splits a compound or joins a range. A run of
whitespace is a single space token rather than one per
character, because the meaningful unit is the gap, not each
blank in it, and everything the first three rules do not claim,
a bracket, an underscore, an accented letter outside the
ASCII word rule, becomes a one-character symbol token so the
tiling stays complete. The kinds are plain strings rather than
an enumeration, because a token stream is data other tools
filter and count, and a string kind is the thing a caller can
match without importing a vocabulary.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN = re.compile(
    r"(?P<number>\d+(?:\.\d+)?)"
    r"|(?P<word>[A-Za-z][A-Za-z']*)"
    r"|(?P<space>\s+)"
    r"|(?P<symbol>.)",
    re.DOTALL,
)


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    start: int
    end: int


def tokenize(text: str) -> list[Token]:
    return [
        Token(
            kind=match.lastgroup,
            text=match.group(0),
            start=match.start(),
            end=match.end(),
        )
        for match in TOKEN.finditer(text)
    ]


def of_kind(text: str, kind: str) -> list[Token]:
    return [token for token in tokenize(text) if token.kind == kind]


def counts(text: str) -> dict[str, int]:
    tally: dict[str, int] = {}
    for token in tokenize(text):
        tally[token.kind] = tally.get(token.kind, 0) + 1
    return tally


def words(text: str) -> list[str]:
    return [token.text for token in of_kind(text, "word")]


def numbers(text: str) -> list[str]:
    return [token.text for token in of_kind(text, "number")]


def render(text: str) -> str:
    found = tokenize(text)
    if not found:
        return "empty text; no tokens"
    return " ".join(f"{token.kind}:{token.text!r}" for token in found)
