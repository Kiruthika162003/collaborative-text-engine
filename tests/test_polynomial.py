from __future__ import annotations

from loom.polynomial import add, derivative, evaluate, multiply


class TestEvaluate:
    def test_horner(self):
        # 1 + 2x + 3x^2 at x = 2 is 1 + 4 + 12
        assert evaluate([1, 2, 3], 2) == 17

    def test_the_constant(self):
        assert evaluate([5], 100) == 5


class TestAdd:
    def test_different_degrees(self):
        assert add([1, 2], [3, 4, 5]) == [4, 6, 5]

    def test_cancellation_trims(self):
        assert add([1, 2], [0, -2]) == [1]


class TestMultiply:
    def test_binomial_square(self):
        # (x + 1)^2 = x^2 + 2x + 1
        assert multiply([1, 1], [1, 1]) == [1, 2, 1]

    def test_by_a_constant(self):
        assert multiply([1, 2, 3], [2]) == [2, 4, 6]


class TestDerivative:
    def test_power_rule(self):
        # d/dx (5 + 3x + 2x^2) = 3 + 4x
        assert derivative([5, 3, 2]) == [3, 4]

    def test_a_constant_has_zero_derivative(self):
        assert derivative([7]) == [0]
