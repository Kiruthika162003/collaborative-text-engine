"""Number detect: find numeric literals in text and classify each by its surface form.

Prose is full of numbers wearing different clothes, and this
finds them and names what each is by how it is written: a bare
integer, a decimal with a point, a grouped integer with
thousands commas, a percentage with a trailing sign, and a
currency amount with a leading dollar. The classification is by
surface, not by meaning, and that is the honest framing: fifty
percent is classified as a percentage because it is written as
one, and its value is reported as the face number fifty rather
than the fraction one half, because dividing it would be
interpreting the number and this only reads it. Where a token
could be more than one kind, a dollar amount that also has a
decimal, the more specific costume wins, currency over decimal,
because the dollar sign is the stronger signal of what the
writer meant. The value returned is the number with its commas
and its currency and percent marks stripped, so a caller can
sum or compare the figures a document mentions without
re-parsing them. It reads numeric literals only and leaves the
dates to the date finder, the ordinals to the ordinal module,
and the Roman numerals to theirs, because each of those is a
number that is not a plain numeral and lumping them together
would be a classifier that agreed with none of the specialists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


@dataclass(frozen=True)
class Number:
    text: str
    kind: str
    value: float
    position: int


def _classify(token: str) -> str:
    if token.startswith("$"):
        return "currency"
    if token.endswith("%"):
        return "percent"
    core = token.strip("$%")
    if "." in core:
        return "decimal"
    if "," in core:
        return "grouped"
    return "integer"


def find_numbers(text: str) -> list[Number]:
    found = []
    for match in TOKEN.finditer(text):
        token = match.group(0)
        core = token.strip("$%").replace(",", "")
        found.append(
            Number(
                text=token,
                kind=_classify(token),
                value=float(core),
                position=match.start(),
            )
        )
    return found


def of_kind(text: str, kind: str) -> list[Number]:
    return [number for number in find_numbers(text) if number.kind == kind]


def total(text: str) -> float:
    return sum(number.value for number in find_numbers(text))
