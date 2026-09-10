"""Graycode: an ordering of the integers where each step flips exactly one bit.

The reflected binary Gray code is a way of numbering the integers
so that consecutive numbers differ in exactly one bit, unlike
ordinary binary where a single increment can flip many bits at once,
as three to four flips three. That single-bit-change property is
what Gray code is for: in hardware where several bits cannot change
at precisely the same instant, ordinary counting can glitch through
wrong intermediate values as the bits settle, while Gray code never
does because only one bit ever moves. Encoding an integer to its Gray
code is startlingly simple, exclusive-or the number with itself
shifted right by one, and that is the whole operation. I had guessed
decoding, going from a Gray code back to the integer, would be just
as simple and symmetric; it is not, and the asymmetry is the
interesting part. Decoding cannot be a single shifted exclusive-or,
because each bit of the original number depends on all the higher
bits of the code, so it has to fold the code down, exclusive-oring
in every rightward shift until nothing is left, accumulating the
higher bits' influence into each lower one. So the forward direction
is one operation and the reverse is a loop, which surprised me for a
transform whose encode looked so trivial that the decode ought to
mirror it. The two are exact inverses over all non-negative integers,
and laying out the codes for the numbers zero upward gives a sequence
in which every adjacent pair, and the pair wrapping from last back to
first, differs by one bit, which is the property the whole
construction exists to guarantee.
"""

from __future__ import annotations

from loom.errors import Invalid


def to_gray(number: int) -> int:
    if number < 0:
        raise Invalid("Gray code is defined for non-negative integers")
    return number ^ (number >> 1)


def from_gray(code: int) -> int:
    if code < 0:
        raise Invalid("a Gray code is non-negative")
    number = 0
    while code:
        number ^= code
        code >>= 1
    return number


def sequence(bits: int) -> list[int]:
    if bits < 0:
        raise Invalid("the bit width must be non-negative")
    return [to_gray(index) for index in range(1 << bits)]
