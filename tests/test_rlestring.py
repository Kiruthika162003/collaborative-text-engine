from __future__ import annotations

import random

import pytest

from loom.errors import Invalid
from loom.rlestring import decode, encode, run_count


class TestEncode:
    def test_a_runny_string(self):
        assert encode("aaabbc") == [("a", 3), ("b", 2), ("c", 1)]

    def test_no_repeats(self):
        assert encode("abc") == [("a", 1), ("b", 1), ("c", 1)]

    def test_the_empty_string(self):
        assert encode("") == []


class TestRoundTrip:
    def test_known(self):
        assert decode(encode("aaabbbcccd")) == "aaabbbcccd"

    def test_random_round_trips(self):
        rng = random.Random(47)
        for _ in range(300):
            text = "".join(rng.choice("aab") for _ in range(rng.randint(0, 40)))
            assert decode(encode(text)) == text


class TestShape:
    def test_long_runs_shrink_the_run_count(self):
        assert run_count("a" * 100) == 1

    def test_no_repeats_gives_a_run_per_character(self):
        assert run_count("abcdef") == 6


class TestGuards:
    def test_a_zero_run_is_refused(self):
        with pytest.raises(Invalid):
            decode([("a", 0)])

    def test_a_multi_character_run_is_refused(self):
        with pytest.raises(Invalid):
            decode([("ab", 2)])
