from __future__ import annotations

import random

from loom.squeeze import squeeze, token_count, unsqueeze


class TestRoundTrip:
    def test_a_battery_of_texts(self):
        for text in [
            "the quick brown fox",
            "mississippi",
            "collaborative text engine converges",
            "a",
            "abracadabra abracadabra",
        ]:
            alphabet, tokens = squeeze(text)
            assert unsqueeze(alphabet, tokens) == text

    def test_the_empty_text(self):
        alphabet, tokens = squeeze("")
        assert unsqueeze(alphabet, tokens) == ""

    def test_random_round_trips(self):
        rng = random.Random(6)
        for _ in range(300):
            text = "".join(rng.choice("abc ") for _ in range(rng.randint(0, 40)))
            alphabet, tokens = squeeze(text)
            assert unsqueeze(alphabet, tokens) == text


class TestCompression:
    def test_repetitive_text_shrinks(self):
        text = "ab" * 60
        assert token_count(text) < len(text)

    def test_a_long_single_run(self):
        text = "a" * 100
        # the whole run collapses to a handful of tokens
        assert token_count(text) < 10


class TestZeroRunAmbiguity:
    def test_a_lone_zero_survives_round_trip(self):
        # Text engineered to leave isolated non-repeats among runs.
        text = "abcabcxyz"
        alphabet, tokens = squeeze(text)
        assert unsqueeze(alphabet, tokens) == text
