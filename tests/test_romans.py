from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.romans import find_romans, from_roman, is_roman, to_roman


class TestEncode:
    def test_subtractive_forms_encode(self):
        assert to_roman(4) == "IV"
        assert to_roman(9) == "IX"
        assert to_roman(1990) == "MCMXC"

    def test_a_full_year_encodes(self):
        assert to_roman(2024) == "MMXXIV"

    def test_out_of_range_is_refused(self):
        with pytest.raises(Invalid):
            to_roman(4000)
        with pytest.raises(Invalid):
            to_roman(0)


class TestDecode:
    def test_canonical_numerals_decode(self):
        assert from_roman("IV") == 4
        assert from_roman("MMXXIV") == 2024

    def test_decoding_is_case_insensitive(self):
        assert from_roman("mix") == 1009

    def test_a_non_canonical_form_is_refused(self):
        with pytest.raises(Invalid):
            from_roman("IIII")
        with pytest.raises(Invalid):
            from_roman("IC")

    def test_an_empty_string_is_refused(self):
        with pytest.raises(Invalid):
            from_roman("")


class TestIsRoman:
    def test_a_valid_numeral_reports_true(self):
        assert is_roman("XIV")

    def test_a_non_numeral_reports_false(self):
        assert not is_roman("hello")

    def test_a_word_that_is_a_valid_numeral_reads_as_one(self):
        # MIX is one thousand and nine; a numeral detector
        # cannot tell the word from the number, a named limit
        assert is_roman("MIX")


class TestFind:
    def test_numerals_in_prose_are_found(self):
        assert find_romans("Chapter IV and section IX") == [
            ("IV", 4),
            ("IX", 9),
        ]

    def test_plain_words_are_not_numerals(self):
        assert find_romans("the plan for today") == []
