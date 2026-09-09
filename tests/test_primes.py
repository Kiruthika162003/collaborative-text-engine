from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.primes import is_prime, next_prime, prime_factors, sieve


class TestIsPrime:
    def test_small_primes(self):
        assert all(is_prime(n) for n in [2, 3, 5, 7, 11, 13])

    def test_composites(self):
        assert not any(is_prime(n) for n in [1, 4, 9, 15, 21])

    def test_below_two(self):
        assert not is_prime(0)
        assert not is_prime(-7)


class TestSieve:
    def test_primes_up_to_ten(self):
        assert sieve(10) == [2, 3, 5, 7]

    def test_a_small_limit(self):
        assert sieve(1) == []


class TestFactors:
    def test_a_composite_factorizes(self):
        assert prime_factors(12) == [2, 2, 3]

    def test_a_prime_is_its_own_factor(self):
        assert prime_factors(17) == [17]

    def test_the_product_returns_the_input(self):
        factors = prime_factors(360)
        product = 1
        for factor in factors:
            product *= factor
        assert product == 360

    def test_below_two_is_refused(self):
        with pytest.raises(Invalid):
            prime_factors(1)


class TestNextPrime:
    def test_from_a_prime(self):
        assert next_prime(13) == 17

    def test_from_a_composite(self):
        assert next_prime(14) == 17
