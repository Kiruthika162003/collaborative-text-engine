"""Number base: convert integers between decimal and any base from two to thirty-six.

Numbers are written in different bases, binary and octal and
hexadecimal most often, and this converts an integer to a base
and reads it back, over the whole range a single case of digits
supports, two through thirty-six, using the ten digits and the
twenty-six lowercase letters. Encoding is repeated division,
peeling off the least significant digit each step, and decoding
is the reverse, accumulating value digit by digit; the two are
exact inverses, so a number written in a base and read back is
the number it started from, the property that lets a base be a
storage or display choice without risking the value. A negative
integer carries its sign through both directions, since a base
is a way of writing magnitude and the sign is separate, and
zero is the single digit zero rather than an empty string, the
honest floor. The base is validated to the two-through-thirty-
six range a single alphabet of digits reaches, and a base
outside it is refused rather than silently clamped, because a
caller asking for base one or base forty has a bug the refusal
points at. Decoding refuses a digit the base does not have, an f
in a base-ten number or a 2 in binary, rather than reading past
it, because a digit out of range is a malformed number and
accepting it would return a value the string does not actually
denote. Decoding folds case, so a hexadecimal FF reads the same
as ff, since the letters are digits and their case is not
meaningful in a number.
"""

from __future__ import annotations

from loom.errors import Invalid

DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def to_base(number: int, base: int) -> str:
    if not 2 <= base <= 36:
        raise Invalid(f"base {base} is outside 2..36")
    if number == 0:
        return "0"
    negative = number < 0
    magnitude = abs(number)
    out = []
    while magnitude:
        magnitude, remainder = divmod(magnitude, base)
        out.append(DIGITS[remainder])
    return ("-" if negative else "") + "".join(reversed(out))


def from_base(text: str, base: int) -> int:
    if not 2 <= base <= 36:
        raise Invalid(f"base {base} is outside 2..36")
    body = text.strip().lower()
    negative = body.startswith("-")
    if negative:
        body = body[1:]
    if not body:
        raise Invalid("no digits to read")
    value = 0
    for char in body:
        digit = DIGITS.find(char)
        if digit < 0 or digit >= base:
            raise Invalid(f"{char!r} is not a base-{base} digit")
        value = value * base + digit
    return -value if negative else value
