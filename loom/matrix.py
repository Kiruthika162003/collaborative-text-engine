"""Matrix: the basic operations on rectangular matrices of numbers.

A matrix here is a list of equal-length rows, and this provides
the operations linear algebra starts from: transpose, which
flips rows and columns so an m-by-n matrix becomes n-by-m;
multiply, the row-by-column product that is the heart of the
subject; addition, element by element; scalar multiplication;
and the identity, the square matrix that leaves any matrix
unchanged when multiplied by it. The dimension rules are
enforced rather than assumed, because a matrix operation on
mismatched shapes is a bug that a silent wrong-shaped result
would carry downstream: multiply refuses when the first
matrix's column count does not equal the second's row count,
the exact condition the product needs, and addition refuses
matrices of different shapes. Those refusals name the shapes
involved, so a caller sees not just that the shapes were wrong
but what they were, which is usually enough to spot the
transpose that was forgotten. The multiply is the plain triple
loop, the definition rather than a fast blocked algorithm,
because these are the small matrices a caller composes by hand,
not the large ones a numerical library exists for, and the
definition is the one that is obviously correct and easy to
check against a worked example. Everything returns a new matrix
and mutates nothing, so a chain of operations leaves its inputs
intact, and the elements are whatever numbers the caller
supplied, integers staying integers through operations that
keep them whole, since the operations are the arithmetic the
elements already support.
"""

from __future__ import annotations

from loom.errors import Invalid

Matrix = list[list[float]]


def _shape(matrix: Matrix) -> tuple[int, int]:
    return (len(matrix), len(matrix[0]) if matrix else 0)


def transpose(matrix: Matrix) -> Matrix:
    rows, cols = _shape(matrix)
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    left_rows, left_cols = _shape(left)
    right_rows, right_cols = _shape(right)
    if left_cols != right_rows:
        raise Invalid(
            f"cannot multiply {left_rows}x{left_cols} by "
            f"{right_rows}x{right_cols}"
        )
    return [
        [
            sum(left[r][k] * right[k][c] for k in range(left_cols))
            for c in range(right_cols)
        ]
        for r in range(left_rows)
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    if _shape(left) != _shape(right):
        raise Invalid(
            f"cannot add {_shape(left)} and {_shape(right)}"
        )
    return [
        [a + b for a, b in zip(row_left, row_right, strict=True)]
        for row_left, row_right in zip(left, right, strict=True)
    ]


def scale(matrix: Matrix, factor: float) -> Matrix:
    return [[value * factor for value in row] for row in matrix]


def identity(size: int) -> Matrix:
    return [
        [1 if r == c else 0 for c in range(size)] for r in range(size)
    ]
