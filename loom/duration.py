"""Duration: format a span of seconds as days, hours, minutes, and back again.

A duration in raw seconds means nothing to a reader, so this
formats it into the units people count in, days, hours,
minutes, seconds, from the largest that fits down, omitting the
zero units so an even hour reads as one hour and not one hour
zero minutes zero seconds. Parsing is the inverse, reading a
string of number-unit pairs back to seconds, so a duration
formatted for display and parsed back returns the same span.
It stops at the day, and that boundary is deliberate and
stated: a week is a fixed seven days and could be added, but a
month and a year are not fixed lengths, a month being anywhere
from twenty-eight to thirty-one days, so formatting a duration
into months would either lie about the length or need a
calendar and a start date this has no business holding. Days
are the largest honest fixed unit, and a caller who thinks in
weeks can divide. Zero is a real duration and formats as zero
seconds rather than an empty string, and a negative span is
refused, because time elapsed does not run backwards and a
negative duration is almost always a subtraction done in the
wrong order that a caller wants to see rather than have
formatted into a confusing minus. The brief helper gives just
the largest unit for a rough by-the-way figure, where the full
breakdown would be more precision than the sentence wants.
"""

from __future__ import annotations

import re

from loom.errors import Invalid

UNITS = (("d", 86400), ("h", 3600), ("m", 60), ("s", 1))
SIZES = dict(UNITS)
PAIR = re.compile(r"(\d+)\s*([dhms])")


def format_duration(seconds: int) -> str:
    if seconds < 0:
        raise Invalid("a duration does not run backwards")
    if seconds == 0:
        return "0s"
    parts = []
    remaining = int(seconds)
    for suffix, size in UNITS:
        quantity, remaining = divmod(remaining, size)
        if quantity:
            parts.append(f"{quantity}{suffix}")
    return " ".join(parts)


def parse_duration(text: str) -> int:
    total = 0
    found = False
    for match in PAIR.finditer(text):
        found = True
        total += int(match.group(1)) * SIZES[match.group(2)]
    if not found:
        raise Invalid(f"{text!r} holds no duration units")
    return total


def brief(seconds: int) -> str:
    if seconds < 0:
        raise Invalid("a duration does not run backwards")
    if seconds == 0:
        return "0s"
    for suffix, size in UNITS:
        if seconds >= size:
            return f"{seconds // size}{suffix}"
    return "0s"
