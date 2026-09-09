from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.numberformat import group, humanize, percent, ungroup


class TestGroup:
    def test_thousands_are_separated(self):
        assert group(1234567) == "1,234,567"

    def test_a_small_number_is_unchanged(self):
        assert group(999) == "999"

    def test_a_negative_keeps_its_sign(self):
        assert group(-1000) == "-1,000"

    def test_a_custom_separator_is_used(self):
        assert group(1000, separator=" ") == "1 000"


class TestUngroup:
    def test_grouping_round_trips(self):
        assert ungroup(group(1234567)) == 1234567

    def test_a_bad_string_is_refused(self):
        with pytest.raises(Invalid):
            ungroup("12x34")


class TestPercent:
    def test_a_fraction_becomes_a_percentage(self):
        assert percent(0.5) == "50%"

    def test_decimals_are_honoured(self):
        assert percent(0.1234, 1) == "12.3%"


class TestHumanize:
    def test_thousands_abbreviate(self):
        assert humanize(1500) == "1.5K"

    def test_millions_abbreviate(self):
        assert humanize(2_500_000) == "2.5M"

    def test_billions_abbreviate(self):
        assert humanize(1_000_000_000) == "1.0B"

    def test_small_numbers_stay_whole(self):
        assert humanize(999) == "999"
