"""Linsolve: solve a linear system exactly by Gaussian elimination over rationals.

A system of linear equations, so many unknowns constrained by that
many equations, is solved by elimination: use one equation to
remove an unknown from all the others, repeat down the unknowns
until each equation names only one, and read the answers off. That
is Gaussian elimination, carried out here on the matrix of
coefficients with the right-hand side carried alongside as an extra
column, eliminating each column both below and above the pivot so
the matrix ends diagonal and the solution divides straight out. The
one judgement in it is choosing the pivot, the equation used to
clear a column: it has to have a nonzero coefficient there, and if
no remaining equation does, the column is unconstrained and the
system has no unique solution, which this reports rather than
dividing by zero. I had guessed floating point would be fine for
small systems; it is not, and the reason is sharper than general
mistrust of floats. Rounding accumulates through the eliminations
so that an exact answer like one third comes out as a long decimal
a hair off, and worse, a matrix that is exactly singular, that truly
has no unique solution, can round into one that merely looks nearly
singular, so the code divides by a tiny nonzero pivot and returns
enormous nonsense instead of reporting the degeneracy. Carrying
exact rationals through the elimination avoids both: the arithmetic
is exact, one third stays one third, and a singular column is
exactly zero and detected as such rather than blurred into a small
number. The trade is speed, exact rationals grow larger numerators
and denominators as the elimination proceeds and are slower than
machine floats, so this is for small systems where being exactly
right matters more than being fast, which is the honest scope. The
same elimination yields the determinant as the product of the
pivots with a sign for the row swaps, zero exactly when the matrix
is singular, which is the same degeneracy the solver refuses.
"""

from __future__ import annotations

from fractions import Fraction

from loom.errors import Invalid


def _augmented(matrix: list, rhs: list) -> list:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise Invalid("the coefficient matrix must be square")
    if len(rhs) != size:
        raise Invalid("the right-hand side must match the number of equations")
    return [
        [Fraction(value) for value in row] + [Fraction(rhs[i])]
        for i, row in enumerate(matrix)
    ]


def solve(matrix: list, rhs: list) -> list:
    size = len(matrix)
    aug = _augmented(matrix, rhs)
    for col in range(size):
        pivot = next((row for row in range(col, size) if aug[row][col] != 0), None)
        if pivot is None:
            raise Invalid("the system is singular and has no unique solution")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        for row in range(size):
            if row != col and aug[row][col] != 0:
                factor = aug[row][col] / aug[col][col]
                aug[row] = [a - factor * b for a, b in zip(aug[row], aug[col], strict=True)]
    return [aug[i][size] / aug[i][i] for i in range(size)]


def determinant(matrix: list) -> Fraction:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise Invalid("the determinant is defined only for a square matrix")
    work = [[Fraction(value) for value in row] for row in matrix]
    result = Fraction(1)
    for col in range(size):
        pivot = next((row for row in range(col, size) if work[row][col] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result = -result
        result *= work[col][col]
        for row in range(col + 1, size):
            if work[row][col] != 0:
                factor = work[row][col] / work[col][col]
                work[row] = [a - factor * b for a, b in zip(work[row], work[col], strict=True)]
    return result
