"""Romans: integers to Roman numerals and back, with the canonical form enforced.

Roman numerals turn up in outlines and page fronts, and this
converts them both ways over the range the standard subtractive
notation covers, one to three thousand nine hundred and
ninety-nine, above which the classic form needs overlines this
does not draw. Encoding is the greedy walk down the value
table that every implementation shares. Decoding is where the
care is: it parses the numeral and then insists on the
canonical form by re-encoding the value and comparing, so IIII
is rejected in favour of IV and IC is rejected in favour of
XCIX, because a decoder that accepted every ambiguous
scribble would let two spellings mean one number and quietly
disagree with its own encoder. The honest limit is the one
every numeral detector meets: some real words are spelled
entirely in numeral letters and parse as valid numerals, MIX
being the clearest, one thousand and nine, so finding numerals
in prose will occasionally flag a word that was never a
number, and that is named rather than pretended away, because
the alternative is a dictionary of exceptions that goes stale.
Detection therefore reports what the rule found and leaves the
judgement to a reader who can see that Chapter MIX is prose,
not a chapter number, which the rule cannot.
"""

from __future__ import annotations

import re

from loom.errors import Invalid

VALUES = (
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
)
TOKEN = re.compile(r"\b[MDCLXVI]+\b", re.IGNORECASE)


def to_roman(number: int) -> str:
    if not 1 <= number <= 3999:
        raise Invalid(
            f"{number} is outside 1..3999; the plain numeral form "
            "does not reach it"
        )
    out = []
    remaining = number
    for value, symbol in VALUES:
        while remaining >= value:
            out.append(symbol)
            remaining -= value
    return "".join(out)


def from_roman(text: str) -> int:
    if not text:
        raise Invalid("an empty string is not a numeral")
    upper = text.upper()
    total = 0
    index = 0
    for value, symbol in VALUES:
        while upper[index : index + len(symbol)] == symbol:
            total += value
            index += len(symbol)
    if index != len(upper) or total == 0 or to_roman(total) != upper:
        raise Invalid(
            f"{text!r} is not a canonical Roman numeral"
        )
    return total


def is_roman(text: str) -> bool:
    try:
        from_roman(text)
    except Invalid:
        return False
    return True


def find_romans(text: str) -> list[tuple[str, int]]:
    found = []
    for match in TOKEN.finditer(text):
        token = match.group(0)
        if is_roman(token):
            found.append((token, from_roman(token)))
    return found
