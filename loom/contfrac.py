"""Contfrac: continued fractions, whose convergents are the best rational approximations.

A continued fraction writes a number as an integer plus one over
an integer plus one over an integer, and so on, and every rational
number has a finite such expansion found by the Euclidean
algorithm: take the whole part, subtract it, invert the leftover
fraction, and repeat, the successive whole parts being the terms.
The expansion is exact and reverses exactly, folding the terms back
from the innermost outward reconstructs the original fraction with
nothing lost. The reason continued fractions are worth more than a
curiosity is their convergents, the fractions you get by stopping
the expansion early. Each convergent is computed from the two
before it by a simple recurrence, and each is the best rational
approximation of the number for its size, meaning no fraction with
a denominator that small comes closer, which is a real theorem, not
a heuristic. I had assumed a decimal was already the natural best
way to pin a number down with a simple fraction, that rounding the
decimal and reading it as a fraction was as good as it got; it is
not, and the gap is stark. The convergents of a number are the
famously good approximations that truncating its decimal never
produces, the way twenty-two sevenths and three hundred
fifty-five over a hundred thirteen fall straight out of the
expansion of the circle constant as approximations far better than
any fraction of similar complexity, while chopping its decimal
gives a fraction with a needlessly huge denominator for the
accuracy it buys. So the continued fraction, not the decimal, is
where the best simple fractions live, and the convergents alternate
around the value, each overshooting a little less than the last
undershot, closing in from both sides. This works over exact
rationals so the expansion and its convergents are exact rather
than a float's approximation of an approximation, and the terms
after the first are positive by construction, the whole-part step
using the floor so a negative number expands cleanly rather than
producing a malformed expansion.
"""

from __future__ import annotations

from fractions import Fraction

from loom.errors import Invalid


def expansion(value: object) -> list[int]:
    fraction = Fraction(value)
    numerator = fraction.numerator
    denominator = fraction.denominator
    terms = []
    while denominator != 0:
        whole = numerator // denominator
        terms.append(whole)
        numerator, denominator = denominator, numerator - whole * denominator
    return terms


def from_terms(terms: list[int]) -> Fraction:
    if not terms:
        raise Invalid("a continued fraction needs at least one term")
    result = Fraction(terms[-1])
    for term in reversed(terms[:-1]):
        result = term + 1 / result
    return result


def convergents(terms: list[int]) -> list[Fraction]:
    if not terms:
        raise Invalid("a continued fraction needs at least one term")
    numerator_back2, numerator_back1 = 0, 1
    denominator_back2, denominator_back1 = 1, 0
    out = []
    for term in terms:
        numerator = term * numerator_back1 + numerator_back2
        denominator = term * denominator_back1 + denominator_back2
        out.append(Fraction(numerator, denominator))
        numerator_back2, numerator_back1 = numerator_back1, numerator
        denominator_back2, denominator_back1 = denominator_back1, denominator
    return out


def convergent_within(value: object, max_denominator: int) -> Fraction:
    if max_denominator < 1:
        raise Invalid("the denominator bound must be at least one")
    terms = expansion(value)
    best = Fraction(terms[0])
    for convergent in convergents(terms):
        if convergent.denominator > max_denominator:
            break
        best = convergent
    return best
