from __future__ import annotations

import pytest

from loom.calc import evaluate
from loom.errors import Invalid


class TestPrecedence:
    def test_times_binds_before_plus(self):
        assert evaluate("1 + 2 * 3") == 7

    def test_parentheses_override(self):
        assert evaluate("(1 + 2) * 3") == 9

    def test_left_to_right_for_same_precedence(self):
        assert evaluate("10 - 3 - 2") == 5


class TestOperators:
    def test_division_is_true_division(self):
        assert evaluate("10 / 4") == 2.5

    def test_unary_minus(self):
        assert evaluate("-5 + 3") == -2

    def test_decimals(self):
        assert evaluate("1.5 * 2") == 3.0


class TestErrors:
    def test_division_by_zero_is_refused(self):
        with pytest.raises(Invalid):
            evaluate("1 / 0")

    def test_a_missing_parenthesis_is_refused(self):
        with pytest.raises(Invalid):
            evaluate("(1 + 2")

    def test_a_stray_symbol_is_refused(self):
        with pytest.raises(Invalid):
            evaluate("1 + @")

    def test_trailing_tokens_are_refused(self):
        with pytest.raises(Invalid):
            evaluate("1 2")
