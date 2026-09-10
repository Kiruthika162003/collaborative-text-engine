from __future__ import annotations

import random

import pytest

from loom.bwt import inverse as bwt_inverse
from loom.bwt import transform as bwt_transform
from loom.errors import Invalid
from loom.mtf import decode, encode


class TestRoundTrip:
    def test_ordinary_text(self):
        alphabet, codes = encode("the quick brown fox")
        assert decode(alphabet, codes) == "the quick brown fox"

    def test_the_code_count_matches_the_length(self):
        text = "mississippi"
        _, codes = encode(text)
        assert len(codes) == len(text)

    def test_random_round_trips(self):
        rng = random.Random(4)
        for _ in range(200):
            text = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 30)))
            alphabet, codes = encode(text)
            assert decode(alphabet, codes) == text


class TestSmallNumbers:
    def test_a_run_becomes_zeros(self):
        _, codes = encode("aaaa")
        assert codes == [0, 0, 0, 0]

    def test_the_first_symbol_is_its_alphabet_position(self):
        # "b" sits at index 1 of sorted {a,b}, so it codes as 1 first.
        _, codes = encode("ba")
        assert codes[0] == 1


class TestPairedWithBwt:
    def test_bwt_then_mtf_round_trips(self):
        text = "the collaborative text engine converges"
        encoded = bwt_transform(text)
        alphabet, codes = encode(encoded)
        assert bwt_inverse(decode(alphabet, codes)) == text


class TestGuards:
    def test_an_out_of_range_code_is_refused(self):
        with pytest.raises(Invalid):
            decode("ab", [5])
