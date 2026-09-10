"""Adler-32: a checksum that is faster than a CRC and weaker, two running sums modulo a prime.

Adler-32 is a checksum built from two running sums taken as the
bytes go by. The first sum is just the total of all the byte values,
and the second is the total of that first sum after each byte, so
the second accumulates the first over and over and therefore depends
on the order of the bytes, not only on their multiset. Both are kept
modulo the largest prime below sixty-five thousand, which is what
makes the arithmetic cheap and the choice of a prime what spreads the
values out, and the checksum is the two sums packed into one number,
the second in the high half and the first in the low. It was designed
as a faster alternative to a cyclic redundancy check, and the trade
is exactly that: it is quicker to compute because it is only
additions and a modulo rather than the bit-level polynomial division
a CRC does, and it is weaker, catching fewer of the error patterns a
CRC is built to catch, particularly on very short inputs where the
sums have not grown enough to mix well. I had guessed a checksum this
simple would be about as reliable as a CRC for detecting damage; it
is not, and the difference is the point of having both, the CRC
spending more effort for stronger detection and Adler-32 spending
less for speed where a weaker check is acceptable. The first sum
starts at one rather than zero, a detail that lets the checksum
distinguish inputs that differ only by leading zero bytes, which a
sum starting at zero would miss, and this produces the same value the
standard library's implementation does so it can be checked against
it.
"""

from __future__ import annotations

_MOD = 65521


def adler32(data: bytes) -> int:
    low = 1
    high = 0
    for byte in data:
        low = (low + byte) % _MOD
        high = (high + low) % _MOD
    return (high << 16) | low
