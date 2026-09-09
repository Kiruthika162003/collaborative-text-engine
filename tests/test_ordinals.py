from __future__ import annotations

from loom.ordinals import find_ordinals, misspelled, ordinal


class TestOrdinal:
    def test_the_basic_suffixes(self):
        assert ordinal(1) == "1st"
        assert ordinal(2) == "2nd"
        assert ordinal(3) == "3rd"
        assert ordinal(4) == "4th"

    def test_the_teens_take_th(self):
        assert ordinal(11) == "11th"
        assert ordinal(12) == "12th"
        assert ordinal(13) == "13th"

    def test_larger_numbers_follow_the_last_digit(self):
        assert ordinal(21) == "21st"
        assert ordinal(113) == "113th"
        assert ordinal(102) == "102nd"


class TestFind:
    def test_correct_ordinals_are_found(self):
        assert find_ordinals("the 1st and 22nd of May") == [
            ("1st", 1),
            ("22nd", 22),
        ]

    def test_a_plain_number_is_not_an_ordinal(self):
        assert find_ordinals("there are 42 items") == []


class TestMisspelled:
    def test_a_wrong_suffix_is_caught(self):
        assert misspelled("the 3th time") == [("3th", "3rd")]

    def test_a_teen_error_is_caught(self):
        assert misspelled("the 21th day") == [("21th", "21st")]

    def test_correct_ordinals_are_not_flagged(self):
        assert misspelled("1st 2nd 3rd 11th") == []
