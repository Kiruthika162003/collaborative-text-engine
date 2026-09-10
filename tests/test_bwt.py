from __future__ import annotations

import random

import pytest

from loom.bwt import SENTINEL, inverse, transform
from loom.errors import Invalid


class TestTransform:
    def test_banana(self):
        assert transform("banana") == "annb" + SENTINEL + "aa"

    def test_the_marker_appears_once(self):
        encoded = transform("mississippi")
        assert encoded.count(SENTINEL) == 1

    def test_similar_contexts_cluster(self):
        # In "mississippi" the transform groups the s runs together.
        encoded = transform("mississippi")
        assert "ss" in encoded


class TestRoundTrip:
    def test_a_battery_of_texts(self):
        for text in [
            "banana",
            "the quick brown fox",
            "mississippi",
            "a",
            "abracadabra",
            "collaborative text engine",
        ]:
            assert inverse(transform(text)) == text

    def test_the_empty_text(self):
        assert inverse(transform("")) == ""

    def test_random_round_trips(self):
        rng = random.Random(5)
        for _ in range(300):
            text = "".join(rng.choice("abc ") for _ in range(rng.randint(0, 30)))
            assert inverse(transform(text)) == text


class TestGuards:
    def test_text_containing_the_marker_is_refused(self):
        with pytest.raises(Invalid):
            transform("bad" + SENTINEL + "text")

    def test_an_empty_transform_is_refused(self):
        with pytest.raises(Invalid):
            inverse("")
