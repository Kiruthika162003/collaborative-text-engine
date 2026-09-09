"""Number format: group digits, ungroup them back, and abbreviate large counts.

Numbers in prose want formatting, and this does the common
kinds without reaching for a locale, which is the point: a
locale grouper is a global setting that surprises a document
written for a different one, so the separator here is the
caller's, a comma by default, applied explicitly. Grouping
walks the digits from the right in threes, the near-universal
convention, and handles a negative by grouping its magnitude
and restoring the sign, and ungrouping is the exact inverse,
stripping the separators to read the integer back, so a number
formatted for display parses cleanly when it comes home. The
percent helper turns a fraction into a percentage with a
chosen number of decimals, the rounding named because a
percentage is a rounded thing and pretending otherwise with a
long tail of digits reads as false precision. The humanize
helper abbreviates a large count to one decimal with a K, M,
or B suffix, the short-scale thousands, millions, billions
that a dashboard uses, and that short scale is stated because
a billion means different magnitudes in different traditions
and a number abbreviator that did not say which it used would
be ambiguous by a factor of a thousand. Everything here is
pure arithmetic on the value, no text scanning, so a caller
composes it with whatever detection they choose rather than
having a detector's opinions baked in.
"""

from __future__ import annotations

from loom.errors import Invalid


def group(number: int, separator: str = ",") -> str:
    sign = "-" if number < 0 else ""
    digits = str(abs(int(number)))
    parts = []
    while len(digits) > 3:
        parts.insert(0, digits[-3:])
        digits = digits[:-3]
    parts.insert(0, digits)
    return sign + separator.join(parts)


def ungroup(text: str, separator: str = ",") -> int:
    stripped = text.replace(separator, "").strip()
    try:
        return int(stripped)
    except ValueError as wrong:
        raise Invalid(f"{text!r} is not a grouped integer") from wrong


def percent(fraction: float, places: int = 0) -> str:
    return f"{fraction * 100:.{places}f}%"


def humanize(number: int) -> str:
    sign = "-" if number < 0 else ""
    magnitude = abs(number)
    for divisor, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if magnitude >= divisor:
            return f"{sign}{magnitude / divisor:.1f}{suffix}"
    return f"{sign}{magnitude}"
