"""Karatsuba: multiply large integers with three half-size products instead of four.

Multiplying two long integers the schoolbook way multiplies every
digit of one by every digit of the other, which is quadratic in the
number of digits, and that looks fundamental: the product genuinely
depends on every pair of digits. Karatsuba shows the quadratic bound
is not fundamental. Split each number into a high half and a low
half, so multiplying them expands into four half-size products, the
high times high, the two cross products, and the low times low. The
insight is that the two cross products are only ever needed added
together, and their sum can be recovered from a single extra
multiplication: multiply the sum of each number's two halves, and
subtract off the high-high and low-low products already computed,
and what remains is exactly the combined cross term. So three
half-size multiplications suffice where four seemed required, and
applied recursively that turns the four-way branching into three-way,
dropping the exponent from two to about one and a half eight five,
the logarithm of three in base two. I had assumed multiplying
n-digit numbers had to be n-squared because the answer touches every
digit pair; it does touch them, but not one multiplication per pair,
because the algebra folds the two cross terms into one product, which
is the first and most surprising sign that the obvious cost of an
operation is not always its real cost. The gain is asymptotic, so it
only pays past a size where the extra additions and the recursion's
overhead are worth avoiding a multiplication, and below that
threshold the plain multiply is faster, which is why this hands off
to the built-in multiplication for small operands rather than
recursing all the way down. Splitting is by bits rather than decimal
digits so the halving is a shift, and signs are handled by
multiplying magnitudes and restoring the sign at the end, since the
split assumes non-negative halves.
"""

from __future__ import annotations

_THRESHOLD = 1 << 16


def _karatsuba(x: int, y: int) -> int:
    if x < _THRESHOLD or y < _THRESHOLD:
        return x * y
    half = max(x.bit_length(), y.bit_length()) // 2
    high_x, low_x = divmod(x, 1 << half)
    high_y, low_y = divmod(y, 1 << half)
    low = _karatsuba(low_x, low_y)
    high = _karatsuba(high_x, high_y)
    cross = _karatsuba(low_x + high_x, low_y + high_y) - high - low
    return (high << (2 * half)) + (cross << half) + low


def multiply(x: int, y: int) -> int:
    sign = -1 if (x < 0) != (y < 0) else 1
    return sign * _karatsuba(abs(x), abs(y))
