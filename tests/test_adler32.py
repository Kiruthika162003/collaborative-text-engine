from __future__ import annotations

import random
import zlib

from loom.adler32 import adler32


class TestAdler32:
    def test_the_empty_input(self):
        assert adler32(b"") == 1

    def test_a_known_value(self):
        assert adler32(b"Wikipedia") == zlib.adler32(b"Wikipedia")

    def test_matches_zlib_over_random_bytes(self):
        rng = random.Random(43)
        for _ in range(500):
            data = bytes(rng.randrange(256) for _ in range(rng.randint(0, 200)))
            assert adler32(data) == zlib.adler32(data)

    def test_order_matters(self):
        assert adler32(b"ab") != adler32(b"ba")

    def test_leading_zeros_are_distinguished(self):
        assert adler32(b"\x00abc") != adler32(b"abc")
