"""Character stats: the text counted by kind of character, below the level of words.

Where the prose module counts words and the census counts
strands, this counts the characters themselves by kind:
letters, digits, spaces, punctuation, and everything else,
which is the breakdown that answers a different set of
questions, how dense the punctuation is, whether a field is
all digits, how much of a line is whitespace. The kinds are
decided by the character's own properties, a letter is what
Python calls alphabetic and so covers accented and non-Latin
letters rather than just A to Z, a digit is a decimal digit,
a space is any whitespace including tabs and newlines, and
punctuation is the Unicode punctuation category; whatever
fits none of these, a symbol, a currency mark, falls into
other, so the five counts always sum to the total and nothing
is uncounted. The distinct-character count and the most
common character are reported too, the two figures that hint
at a text's shape without reading it, a document of mostly
one repeated character reading very differently from one that
uses its whole alphabet. It counts what is given, making no
distinction between visible and tombstoned because it works
on a string, not a weave, which is the right level for a
function this general: hand it any text and it tallies it.
"""

from __future__ import annotations

import unicodedata


def counts(text: str) -> dict[str, int]:
    tally = {
        "letters": 0,
        "digits": 0,
        "spaces": 0,
        "punctuation": 0,
        "other": 0,
    }
    for char in text:
        if char.isalpha():
            tally["letters"] += 1
        elif char.isdigit():
            tally["digits"] += 1
        elif char.isspace():
            tally["spaces"] += 1
        elif unicodedata.category(char).startswith("P"):
            tally["punctuation"] += 1
        else:
            tally["other"] += 1
    return tally


def total(text: str) -> int:
    return len(text)


def distinct(text: str) -> int:
    return len(set(text))


def most_common(text: str) -> str | None:
    if not text:
        return None
    frequency: dict[str, int] = {}
    for char in text:
        frequency[char] = frequency.get(char, 0) + 1
    return max(frequency, key=lambda char: (frequency[char], char))


def report(text: str) -> str:
    if not text:
        return "empty text; nothing to count"
    tally = counts(text)
    parts = ", ".join(f"{count} {kind}" for kind, count in tally.items())
    return (
        f"{total(text)} character(s), {distinct(text)} distinct: {parts}"
    )
