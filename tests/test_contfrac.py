from __future__ import annotations

import random
from fractions import Fraction
from itertools import pairwise

import pytest

from loom.contfrac import convergent_within, convergents, expansion, from_terms
from loom.errors import Invalid


class TestExpansion:
    def test_the_classic_example(self):
        assert expansion(Fraction(415, 93)) == [4, 2, 6, 7]

    def test_an_integer(self):
        assert expansion(7) == [7]

    def test_a_simple_fraction(self):
        assert expansion(Fraction(1, 3)) == [0, 3]


class TestRoundTrip:
    def test_from_terms_undoes_expansion(self):
        rng = random.Random(3)
        for _ in range(300):
            numerator = rng.randint(-50, 50)
            denominator = rng.randint(1, 50)
            value = Fraction(numerator, denominator)
            assert from_terms(expansion(value)) == value

    def test_a_hand_built_fraction(self):
        assert from_terms([4, 2, 6, 7]) == Fraction(415, 93)


class TestConvergents:
    def test_the_convergents_of_the_classic(self):
        assert convergents([4, 2, 6, 7]) == [
            Fraction(4),
            Fraction(9, 2),
            Fraction(58, 13),
            Fraction(415, 93),
        ]

    def test_the_last_convergent_is_the_value(self):
        value = Fraction(355, 113)
        assert convergents(expansion(value))[-1] == value

    def test_convergents_alternate_around_the_value(self):
        value = Fraction(415, 93)
        convs = convergents(expansion(value))
        differences = [convergent - value for convergent in convs[:-1]]
        for earlier, later in pairwise(differences):
            assert (earlier > 0) != (later > 0)


class TestApproximation:
    def test_within_a_denominator_bound(self):
        assert convergent_within(Fraction(415, 93), 15) == Fraction(58, 13)

    def test_a_generous_bound_gives_the_exact_value(self):
        assert convergent_within(Fraction(415, 93), 1000) == Fraction(415, 93)

    def test_a_zero_bound_is_refused(self):
        with pytest.raises(Invalid):
            convergent_within(Fraction(1, 2), 0)


class TestGuards:
    def test_from_no_terms_is_refused(self):
        with pytest.raises(Invalid):
            from_terms([])
