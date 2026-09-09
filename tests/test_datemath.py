from __future__ import annotations

import datetime

import pytest

from loom.datemath import (
    add_days,
    day_number,
    days_between,
    from_day_number,
    is_leap,
    weekday,
)
from loom.errors import Invalid


class TestLeap:
    def test_the_rules(self):
        assert is_leap(2000)
        assert not is_leap(1900)
        assert is_leap(2020)
        assert not is_leap(2021)


class TestArithmetic:
    def test_days_between(self):
        assert days_between((2020, 1, 1), (2020, 1, 31)) == 30

    def test_add_across_a_leap_day(self):
        assert add_days((2020, 2, 28), 1) == (2020, 2, 29)

    def test_add_across_a_non_leap_february(self):
        assert add_days((2019, 2, 28), 1) == (2019, 3, 1)

    def test_add_across_a_year(self):
        assert add_days((2020, 12, 31), 1) == (2021, 1, 1)


class TestWeekday:
    def test_it_matches_the_standard_library(self):
        for year, month, day in [(2000, 1, 1), (2020, 2, 29), (1999, 12, 31)]:
            assert weekday(year, month, day) == datetime.date(
                year, month, day
            ).weekday()


class TestConvert:
    def test_the_epoch_is_zero(self):
        assert day_number(1970, 1, 1) == 0

    def test_round_trip(self):
        number = day_number(2023, 7, 15)
        assert from_day_number(number) == (2023, 7, 15)

    def test_an_invalid_date_is_refused(self):
        with pytest.raises(Invalid):
            day_number(2021, 2, 29)
