from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.rpn import eval_postfix, evaluate, to_postfix


class TestPostfix:
    def test_a_simple_sum(self):
        assert eval_postfix("3 4 +") == 7

    def test_a_longer_expression(self):
        assert eval_postfix("5 1 2 + 4 * + 3 -") == 14

    def test_division_by_zero_is_refused(self):
        with pytest.raises(Invalid):
            eval_postfix("1 0 /")

    def test_too_few_operands_is_refused(self):
        with pytest.raises(Invalid):
            eval_postfix("1 +")


class TestConversion:
    def test_precedence(self):
        assert to_postfix("3 + 4 * 2") == "3 4 2 * +"

    def test_parentheses(self):
        assert to_postfix("( 1 + 2 ) * 3") == "1 2 + 3 *"

    def test_a_mismatched_parenthesis_is_refused(self):
        with pytest.raises(Invalid):
            to_postfix("( 1 + 2")


class TestEvaluate:
    def test_infix_through_postfix(self):
        assert evaluate("( 1 + 2 ) * 3") == 9

    def test_precedence_end_to_end(self):
        assert evaluate("2 + 3 * 4") == 14
