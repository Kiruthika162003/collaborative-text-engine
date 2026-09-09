from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.matrix import add, identity, multiply, scale, transpose


class TestTranspose:
    def test_rows_and_columns_flip(self):
        assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


class TestMultiply:
    def test_the_product(self):
        assert multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == [
            [19, 22],
            [43, 50],
        ]

    def test_identity_leaves_a_matrix_unchanged(self):
        matrix = [[1, 2], [3, 4]]
        assert multiply(matrix, identity(2)) == matrix

    def test_a_dimension_mismatch_is_refused(self):
        with pytest.raises(Invalid):
            multiply([[1, 2, 3]], [[1, 2]])


class TestAddAndScale:
    def test_addition(self):
        assert add([[1, 2]], [[3, 4]]) == [[4, 6]]

    def test_a_shape_mismatch_is_refused(self):
        with pytest.raises(Invalid):
            add([[1, 2]], [[1]])

    def test_scaling(self):
        assert scale([[1, 2], [3, 4]], 2) == [[2, 4], [6, 8]]


class TestIdentity:
    def test_identity_shape(self):
        assert identity(3) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
