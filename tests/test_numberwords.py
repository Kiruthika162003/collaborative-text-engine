from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.numberwords import parse_words, spell


class TestSpell:
    def test_small_numbers_spell(self):
        assert spell(0) == "zero"
        assert spell(7) == "seven"
        assert spell(19) == "nineteen"

    def test_compound_tens_are_hyphenated(self):
        assert spell(42) == "forty-two"
        assert spell(90) == "ninety"

    def test_hundreds_and_thousands(self):
        assert spell(100) == "one hundred"
        assert spell(1234) == (
            "one thousand two hundred thirty-four"
        )

    def test_out_of_range_is_refused(self):
        with pytest.raises(Invalid):
            spell(1000000)


class TestParse:
    def test_words_read_back_to_a_number(self):
        assert parse_words("forty-two") == 42
        assert parse_words("one thousand two hundred thirty-four") == 1234

    def test_an_unknown_word_is_refused(self):
        with pytest.raises(Invalid):
            parse_words("three cats")

    def test_an_empty_string_is_refused(self):
        with pytest.raises(Invalid):
            parse_words("   ")


class TestRoundTrip:
    def test_spell_then_parse_is_identity(self):
        for number in [0, 5, 19, 20, 42, 100, 999, 1000, 1234, 90210, 999999]:
            assert parse_words(spell(number)) == number
