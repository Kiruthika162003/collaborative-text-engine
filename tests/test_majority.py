from __future__ import annotations

import random
from collections import Counter

import pytest

from loom.errors import Invalid
from loom.majority import majority, majority_or_none


class TestMajority:
    def test_a_clear_majority(self):
        assert majority([1, 2, 1, 1, 3, 1]) == 1

    def test_the_whole_list_is_one_value(self):
        assert majority(["a", "a", "a"]) == "a"

    def test_no_majority_is_refused(self):
        with pytest.raises(Invalid):
            majority([1, 2, 3, 4])

    def test_exactly_half_is_not_a_majority(self):
        with pytest.raises(Invalid):
            majority([1, 1, 2, 2])

    def test_the_empty_list_is_refused(self):
        with pytest.raises(Invalid):
            majority([])


class TestOrNone:
    def test_returns_none_without_a_majority(self):
        assert majority_or_none([1, 2, 3]) is None
        assert majority_or_none([]) is None

    def test_returns_the_majority_when_present(self):
        assert majority_or_none([5, 5, 5, 1, 2]) == 5


class TestAgainstCounter:
    def test_matches_a_frequency_tally(self):
        rng = random.Random(29)
        for _ in range(500):
            size = rng.randint(1, 40)
            data = [rng.randrange(5) for _ in range(size)]
            counts = Counter(data)
            top, freq = counts.most_common(1)[0]
            expected = top if freq * 2 > size else None
            assert majority_or_none(data) == expected
