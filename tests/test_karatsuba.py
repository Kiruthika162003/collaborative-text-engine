from __future__ import annotations

import random

from loom.karatsuba import multiply


class TestSmall:
    def test_small_products(self):
        assert multiply(0, 5) == 0
        assert multiply(6, 7) == 42
        assert multiply(1, 999) == 999

    def test_signs(self):
        assert multiply(-6, 7) == -42
        assert multiply(6, -7) == -42
        assert multiply(-6, -7) == 42


class TestAgainstBuiltin:
    def test_large_random_products(self):
        rng = random.Random(19)
        for _ in range(500):
            a = rng.randrange(0, 1 << rng.randint(1, 400))
            b = rng.randrange(0, 1 << rng.randint(1, 400))
            assert multiply(a, b) == a * b

    def test_signed_random_products(self):
        rng = random.Random(20)
        for _ in range(500):
            a = rng.randint(-(1 << 200), 1 << 200)
            b = rng.randint(-(1 << 200), 1 << 200)
            assert multiply(a, b) == a * b

    def test_equal_large_operands(self):
        big = (1 << 500) - 1
        assert multiply(big, big) == big * big
