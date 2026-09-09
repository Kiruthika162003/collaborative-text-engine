"""Polynomial: arithmetic on polynomials given as coefficient lists.

A polynomial is represented here as its coefficients from the
constant term up, so the list one, two, three is one plus two x
plus three x squared, the ordering that makes the index the
power and the arithmetic natural. Evaluating uses Horner's
method, nesting the multiplications so a degree-n polynomial
costs n multiplications rather than the powers a term-by-term
sum would compute, and it is both faster and more numerically
stable, the standard way to evaluate a polynomial. Addition adds
the coefficients position by position, padding the shorter with
the zero coefficients it implicitly has, and multiplication is
the convolution of the two coefficient lists, each pair of terms
contributing to the coefficient of their combined power, which
is the definition of multiplying polynomials. The derivative
drops the constant term and multiplies each remaining
coefficient by its power, the power rule applied to the whole
polynomial at once. Results are trimmed of trailing zero
coefficients, so a subtraction that cancels the leading term
returns the lower-degree polynomial it actually is rather than
one padded with a zero leading coefficient that would lie about
its degree, and the zero polynomial is the single zero
coefficient rather than an empty list, the honest representation
of the polynomial that is zero everywhere. The coefficients are
whatever numbers a caller supplies, so the arithmetic works over
integers and floats alike, and everything returns new lists,
leaving the inputs untouched for a caller composing operations.
"""

from __future__ import annotations

Polynomial = list[float]


def _trim(coefficients: Polynomial) -> Polynomial:
    result = list(coefficients)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def evaluate(coefficients: Polynomial, x: float) -> float:
    result: float = 0
    for coefficient in reversed(coefficients):
        result = result * x + coefficient
    return result


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    length = max(len(left), len(right))
    return _trim(
        [
            (left[i] if i < len(left) else 0)
            + (right[i] if i < len(right) else 0)
            for i in range(length)
        ]
    )


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    if not left or not right:
        return [0]
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return _trim(result)


def derivative(coefficients: Polynomial) -> Polynomial:
    if len(coefficients) <= 1:
        return [0]
    return [coefficients[power] * power for power in range(1, len(coefficients))]
