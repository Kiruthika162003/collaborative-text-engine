"""Fraction: exact rational arithmetic, always in lowest terms.

A fraction is a pair of integers, and this keeps them exact
where floating point would round: one third plus one sixth is
exactly one half here, not a decimal that almost is. Every
fraction is stored in lowest terms with a positive denominator,
reduced on construction by dividing out the greatest common
divisor and moving any sign to the numerator, so two fractions
that name the same value are the same fraction, two-quarters
and one-half being equal not merely close, which makes equality
and hashing work the way a caller expects. The four operations
combine two fractions by the schoolbook rules, cross-multiplying
for addition and subtraction and multiplying straight across for
multiplication, and each result is reduced again, so a chain of
operations stays in lowest terms rather than accumulating a
common factor that grows the integers needlessly. A zero
denominator is refused at construction, because a fraction over
zero is not a number and admitting it would let a division by
zero hide inside a value rather than surface where it happened.
Conversion to float is offered for when a decimal is finally
wanted, and it is the one lossy step, named as such: up to that
point the arithmetic is exact, and a caller who needs it exact
stays in fractions and converts once at the end rather than
carrying rounding through every step. The numerator and
denominator are readable, so a caller can render the fraction
however they like, since how a fraction is displayed is a
choice this leaves to them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from loom.errors import Invalid


@dataclass(frozen=True)
class Fraction:
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if self.denominator == 0:
            raise Invalid("a fraction cannot have a zero denominator")
        divisor = math.gcd(self.numerator, self.denominator)
        sign = -1 if self.denominator < 0 else 1
        object.__setattr__(
            self, "numerator", sign * self.numerator // divisor
        )
        object.__setattr__(
            self, "denominator", sign * self.denominator // divisor
        )

    def __add__(self, other: Fraction) -> Fraction:
        return Fraction(
            self.numerator * other.denominator
            + other.numerator * self.denominator,
            self.denominator * other.denominator,
        )

    def __sub__(self, other: Fraction) -> Fraction:
        return Fraction(
            self.numerator * other.denominator
            - other.numerator * self.denominator,
            self.denominator * other.denominator,
        )

    def __mul__(self, other: Fraction) -> Fraction:
        return Fraction(
            self.numerator * other.numerator,
            self.denominator * other.denominator,
        )

    def __truediv__(self, other: Fraction) -> Fraction:
        return Fraction(
            self.numerator * other.denominator,
            self.denominator * other.numerator,
        )

    def __float__(self) -> float:
        return self.numerator / self.denominator

    def __str__(self) -> str:
        return f"{self.numerator}/{self.denominator}"
