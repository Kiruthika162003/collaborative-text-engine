"""Ordinals: format a number as first, second, third, and catch the mis-suffixed ones.

Ordinals have a suffix rule that trips writers and generators
alike: st, nd, rd for one, two, three, th for the rest, except
the teens, where eleventh, twelfth, and thirteenth take th
despite ending in one, two, three. This formats an integer
correctly, honouring that teens exception so 11th and 113th
come out right where a naive rule would write 11st and 113rd,
and it reads ordinals back out of prose. Reading is where it
earns proofreading value: it separates the correctly spelled
ordinals from the mis-suffixed ones, so 3th and 21th are
caught as the errors they are with the spelling they should
have had, which is exactly the slip a hurried writer or a
template with a bad rule produces. It reports rather than
corrects, in the reading-organ tradition, because whether a
1th is a typo for 1st or for something else is occasionally a
judgement, and a detector that silently rewrote would
sometimes rewrite wrong. The formatting is pure arithmetic on
the last one and two digits, no table of exceptions beyond the
teens the rule itself names, so it is correct for any
non-negative integer rather than only the small ones a lookup
table would have covered.
"""

from __future__ import annotations

import re

SUFFIXES = re.compile(r"\b(\d+)(st|nd|rd|th)\b", re.IGNORECASE)


def ordinal(number: int) -> str:
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def find_ordinals(text: str) -> list[tuple[str, int]]:
    found = []
    for match in SUFFIXES.finditer(text):
        value = int(match.group(1))
        if match.group(0).lower() == ordinal(value):
            found.append((match.group(0), value))
    return found


def misspelled(text: str) -> list[tuple[str, str]]:
    wrong = []
    for match in SUFFIXES.finditer(text):
        value = int(match.group(1))
        correct = ordinal(value)
        if match.group(0).lower() != correct:
            wrong.append((match.group(0), correct))
    return wrong
