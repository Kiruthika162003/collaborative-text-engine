from __future__ import annotations

from itertools import pairwise

import pytest

from loom.errors import Invalid
from loom.graycode import from_gray, sequence, to_gray


class TestEncode:
    def test_known_values(self):
        assert [to_gray(n) for n in range(8)] == [0, 1, 3, 2, 6, 7, 5, 4]


class TestRoundTrip:
    def test_encode_then_decode(self):
        for n in range(1000):
            assert from_gray(to_gray(n)) == n


class TestSingleBitChange:
    def test_consecutive_codes_differ_by_one_bit(self):
        codes = sequence(6)
        for earlier, later in pairwise(codes):
            assert bin(earlier ^ later).count("1") == 1

    def test_the_sequence_is_a_permutation(self):
        codes = sequence(5)
        assert sorted(codes) == list(range(32))


class TestGuards:
    def test_a_negative_number_is_refused(self):
        with pytest.raises(Invalid):
            to_gray(-1)

    def test_a_negative_width_is_refused(self):
        with pytest.raises(Invalid):
            sequence(-1)
