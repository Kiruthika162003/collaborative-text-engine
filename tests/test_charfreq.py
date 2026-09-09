from __future__ import annotations

import pytest

from loom.charfreq import distinct, entropy, frequency, most_common


class TestFrequency:
    def test_characters_are_counted(self):
        assert frequency("aab") == {"a": 2, "b": 1}

    def test_most_common_ranks(self):
        assert most_common("aaabbc", 2) == [("a", 3), ("b", 2)]

    def test_distinct_counts_unique(self):
        assert distinct("aabbc") == 3


class TestEntropy:
    def test_one_character_has_zero_entropy(self):
        assert entropy("aaaa") == 0.0

    def test_two_equal_characters_is_one_bit(self):
        assert entropy("ab") == 1.0
        assert entropy("aabb") == 1.0

    def test_four_equal_characters_is_two_bits(self):
        assert entropy("abcd") == pytest.approx(2.0)

    def test_an_empty_text_has_zero_entropy(self):
        assert entropy("") == 0.0
