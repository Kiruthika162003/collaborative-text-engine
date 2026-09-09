"""Bit ops: the small bit-manipulation operations, each by its standard idiom.

Working with the bits of an integer is a set of one-liners that
are easy to get subtly wrong, so this collects them named and
tested. Setting a bit ors in a one shifted to its position,
clearing ands with that mask inverted, toggling xors it, and
testing shifts the bit down and masks it, the four operations
every bit twiddler writes and occasionally writes backwards.
The population count is the number of one bits, and telling
whether a number is a power of two is the elegant trick that a
power of two and one less than it share no bits, so their and is
zero, which is faster and clearer than a loop once seen. The
lowest set bit is isolated by anding the number with its
negation, the two's-complement idiom that leaves only the
rightmost one bit, and its position is that value's bit length
less one. Rotation is width-bounded, because rotating is defined
within a fixed number of bits, a byte or a word, not over
Python's unbounded integers, so it takes the width and wraps the
bits that fall off one end back onto the other within it. The
operations that read or count bits treat the integer as non-
negative, since a negative in two's complement has infinitely
many leading one bits in Python's model and a population count of
that is not a finite number; a caller with a fixed-width
negative masks it to the width first. These are the exact idioms
a caller would write inline, pulled out so they are written once
and correctly, which in bit manipulation is worth more than in
most places, since a wrong shift produces a plausible wrong
number rather than an obvious error.
"""

from __future__ import annotations

from loom.errors import Invalid


def set_bit(number: int, index: int) -> int:
    return number | (1 << index)


def clear_bit(number: int, index: int) -> int:
    return number & ~(1 << index)


def toggle_bit(number: int, index: int) -> int:
    return number ^ (1 << index)


def test_bit(number: int, index: int) -> bool:
    return bool((number >> index) & 1)


def popcount(number: int) -> int:
    if number < 0:
        raise Invalid("popcount is defined for non-negative integers")
    return bin(number).count("1")


def is_power_of_two(number: int) -> bool:
    return number > 0 and (number & (number - 1)) == 0


def lowest_set_bit(number: int) -> int:
    if number == 0:
        return -1
    return (number & -number).bit_length() - 1


def rotate_left(number: int, amount: int, width: int) -> int:
    if width < 1:
        raise Invalid("rotation width must be positive")
    mask = (1 << width) - 1
    value = number & mask
    amount %= width
    return ((value << amount) | (value >> (width - amount))) & mask
