from __future__ import annotations

import pytest

from loom.combinatorics import (
    catalan,
    combinations,
    factorial,
    permutations,
)
from loom.errors import Invalid


class TestFactorial:
    def test_values(self):
        assert factorial(0) == 1
        assert factorial(5) == 120

    def test_a_negative_is_refused(self):
        with pytest.raises(Invalid):
            factorial(-1)


class TestPermutations:
    def test_ordered_selections(self):
        assert permutations(5, 2) == 20
        assert permutations(5, 0) == 1

    def test_choosing_too_many_is_refused(self):
        with pytest.raises(Invalid):
            permutations(3, 5)


class TestCombinations:
    def test_unordered_selections(self):
        assert combinations(5, 2) == 10
        assert combinations(5, 0) == 1

    def test_a_large_binomial_is_exact(self):
        assert combinations(52, 5) == 2598960

    def test_symmetry(self):
        assert combinations(10, 3) == combinations(10, 7)


class TestCatalan:
    def test_values(self):
        assert catalan(0) == 1
        assert catalan(4) == 14

    def test_a_negative_is_refused(self):
        with pytest.raises(Invalid):
            catalan(-1)
