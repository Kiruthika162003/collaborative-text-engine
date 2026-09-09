from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.vector import (
    add,
    cross,
    distance,
    dot,
    magnitude,
    normalize,
    scale,
    subtract,
)


class TestArithmetic:
    def test_add_and_subtract(self):
        assert add([1, 2], [3, 4]) == [4, 6]
        assert subtract([5, 5], [1, 2]) == [4, 3]

    def test_scale(self):
        assert scale([1, 2, 3], 2) == [2, 4, 6]

    def test_a_dimension_mismatch_is_refused(self):
        with pytest.raises(Invalid):
            add([1, 2], [1, 2, 3])


class TestProducts:
    def test_dot(self):
        assert dot([1, 2, 3], [4, 5, 6]) == 32

    def test_cross(self):
        assert cross([1, 0, 0], [0, 1, 0]) == [0, 0, 1]

    def test_cross_needs_three_dimensions(self):
        with pytest.raises(Invalid):
            cross([1, 2], [3, 4])


class TestGeometry:
    def test_magnitude(self):
        assert magnitude([3, 4]) == 5.0

    def test_normalize(self):
        assert normalize([3, 4]) == [0.6, 0.8]

    def test_normalizing_zero_is_refused(self):
        with pytest.raises(Invalid):
            normalize([0, 0])

    def test_distance(self):
        assert distance([0, 0], [3, 4]) == 5.0
