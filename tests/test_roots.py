from __future__ import annotations

import math

import pytest

from loom.errors import Invalid
from loom.roots import bisection, newton, secant


def _square_minus_two(x: float) -> float:
    return x * x - 2


class TestBisection:
    def test_finds_the_square_root_of_two(self):
        root = bisection(_square_minus_two, 0, 2)
        assert abs(root - math.sqrt(2)) < 1e-9

    def test_a_root_at_a_bracket_end(self):
        assert bisection(lambda x: x - 3, 3, 10) == 3

    def test_a_cubic_root(self):
        root = bisection(lambda x: x**3 - x - 2, 1, 2)
        assert abs(root**3 - root - 2) < 1e-9

    def test_a_bracket_without_a_sign_change_is_refused(self):
        with pytest.raises(Invalid):
            bisection(_square_minus_two, 2, 3)


class TestNewton:
    def test_finds_the_square_root_of_two(self):
        root = newton(_square_minus_two, lambda x: 2 * x, 1.0)
        assert abs(root - math.sqrt(2)) < 1e-12

    def test_a_zero_derivative_is_refused(self):
        with pytest.raises(Invalid):
            newton(lambda x: x * x + 1, lambda x: 2 * x, 0.0)

    def test_non_convergence_is_reported(self):
        with pytest.raises(Invalid):
            newton(lambda x: x * x + 1, lambda x: 2 * x, 1.0, max_iterations=5)


class TestSecant:
    def test_finds_the_square_root_of_two(self):
        root = secant(_square_minus_two, 1.0, 2.0)
        assert abs(root - math.sqrt(2)) < 1e-9

    def test_agrees_with_the_other_methods(self):
        f = lambda x: x**3 - x - 2  # noqa: E731
        by_bisection = bisection(f, 1, 2)
        by_secant = secant(f, 1.0, 2.0)
        assert abs(by_bisection - by_secant) < 1e-6
