from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.fraction import Fraction


class TestReduction:
    def test_fractions_are_reduced(self):
        assert Fraction(2, 4) == Fraction(1, 2)

    def test_sign_moves_to_the_numerator(self):
        assert Fraction(1, -2) == Fraction(-1, 2)

    def test_zero_normalizes(self):
        assert Fraction(0, 5) == Fraction(0, 1)

    def test_a_zero_denominator_is_refused(self):
        with pytest.raises(Invalid):
            Fraction(1, 0)


class TestArithmetic:
    def test_addition(self):
        assert Fraction(1, 2) + Fraction(1, 3) == Fraction(5, 6)

    def test_subtraction(self):
        assert Fraction(1, 2) - Fraction(1, 6) == Fraction(1, 3)

    def test_multiplication(self):
        assert Fraction(1, 2) * Fraction(2, 3) == Fraction(1, 3)

    def test_division(self):
        assert Fraction(1, 2) / Fraction(1, 4) == Fraction(2, 1)


class TestConvert:
    def test_to_float(self):
        assert float(Fraction(1, 4)) == 0.25

    def test_str(self):
        assert str(Fraction(3, 4)) == "3/4"
