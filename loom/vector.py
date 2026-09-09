"""Vector: the arithmetic of numeric vectors, addition through cross product.

Vectors are lists of numbers with their own arithmetic, and this
provides it: adding and subtracting element by element, scaling
by a number, the dot product that sums the products and measures
alignment, the magnitude that is the length by Pythagoras,
normalizing to a unit vector in the same direction, the distance
between two points as the magnitude of their difference, and the
cross product that yields a vector perpendicular to two others.
The operations that combine two vectors enforce that they have
the same dimension, because adding a two-vector to a three-vector
is meaningless and a silent result of the shorter or longer would
be a bug carried forward; the mismatch is refused with the two
lengths named. Normalizing the zero vector is refused, because
the zero vector has no direction and dividing by its zero length
would be a division by zero dressed as a geometric operation, so
a caller normalizing a possibly-zero vector checks the magnitude
first or catches the refusal. The cross product is defined only
in three dimensions, where perpendicularity to two vectors picks
out a unique direction, so it refuses vectors of any other
length rather than returning something for a case the operation
does not have. Everything returns new vectors and numbers,
mutating nothing, so a chain of vector operations leaves its
inputs intact, and the components are whatever numbers a caller
supplies, the arithmetic being the numbers' own, which keeps the
vectors general over integers and floats alike.
"""

from __future__ import annotations

import math

from loom.errors import Invalid

Vector = list[float]


def _same(left: Vector, right: Vector) -> None:
    if len(left) != len(right):
        raise Invalid(
            f"dimension mismatch: {len(left)} and {len(right)}"
        )


def add(left: Vector, right: Vector) -> Vector:
    _same(left, right)
    return [a + b for a, b in zip(left, right, strict=True)]


def subtract(left: Vector, right: Vector) -> Vector:
    _same(left, right)
    return [a - b for a, b in zip(left, right, strict=True)]


def scale(vector: Vector, factor: float) -> Vector:
    return [component * factor for component in vector]


def dot(left: Vector, right: Vector) -> float:
    _same(left, right)
    return sum(a * b for a, b in zip(left, right, strict=True))


def magnitude(vector: Vector) -> float:
    return math.sqrt(sum(component * component for component in vector))


def normalize(vector: Vector) -> Vector:
    length = magnitude(vector)
    if length == 0:
        raise Invalid("the zero vector has no direction to normalize")
    return [component / length for component in vector]


def distance(left: Vector, right: Vector) -> float:
    return magnitude(subtract(left, right))


def cross(left: Vector, right: Vector) -> Vector:
    if len(left) != 3 or len(right) != 3:
        raise Invalid("the cross product is defined in three dimensions")
    a1, a2, a3 = left
    b1, b2, b3 = right
    return [a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1]
