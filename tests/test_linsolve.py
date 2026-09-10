from __future__ import annotations

from fractions import Fraction

import pytest

from loom.errors import Invalid
from loom.linsolve import determinant, solve


class TestSolve:
    def test_a_two_by_two_system(self):
        # x + y = 3 ; x - y = 1  ->  x = 2, y = 1
        assert solve([[1, 1], [1, -1]], [3, 1]) == [Fraction(2), Fraction(1)]

    def test_a_system_with_a_fractional_answer(self):
        # 3x = 1  ->  x = 1/3, exactly
        assert solve([[3]], [1]) == [Fraction(1, 3)]

    def test_a_three_by_three_system(self):
        matrix = [
            [2, 1, -1],
            [-3, -1, 2],
            [-2, 1, 2],
        ]
        rhs = [8, -11, -3]
        assert solve(matrix, rhs) == [Fraction(2), Fraction(3), Fraction(-1)]

    def test_the_solution_satisfies_the_equations(self):
        matrix = [[4, 3], [6, 3]]
        rhs = [10, 12]
        x = solve(matrix, rhs)
        for row, target in zip(matrix, rhs, strict=True):
            assert sum(a * b for a, b in zip(row, x, strict=True)) == target


class TestSingular:
    def test_a_singular_system_is_refused(self):
        # second row is a multiple of the first
        with pytest.raises(Invalid):
            solve([[1, 2], [2, 4]], [3, 6])

    def test_a_mismatched_right_hand_side_is_refused(self):
        with pytest.raises(Invalid):
            solve([[1, 2], [3, 4]], [1])


class TestDeterminant:
    def test_known_determinants(self):
        assert determinant([[1, 2], [3, 4]]) == Fraction(-2)
        assert determinant([[2, 0], [0, 3]]) == Fraction(6)

    def test_a_singular_matrix_has_zero_determinant(self):
        assert determinant([[1, 2], [2, 4]]) == Fraction(0)

    def test_the_identity_has_determinant_one(self):
        assert determinant([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == Fraction(1)
