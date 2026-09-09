"""Date math: arithmetic on calendar dates through a day-number conversion.

Doing arithmetic on dates, how many days between two, what date
is a hundred days on, what weekday a date falls, is awkward
directly because months have different lengths and leap years
break the pattern, so this converts a date to a single day
number and does the arithmetic there. The conversion is the
well-known days-from-civil algorithm that maps any proleptic
Gregorian date to the count of days since the first of January
nineteen seventy and back, handling the four-year, hundred-year,
and four-hundred-year leap rules exactly, so a date turned into
a number and back returns unchanged. With dates as numbers the
operations are subtraction and addition: the days between two
dates is the difference of their numbers, and adding days is
adding to the number and converting back, which lands on the
right date across month and year boundaries and leap days
without any special cases. The weekday falls out of the day
number modulo seven, anchored so that the answer matches the
convention where Monday is zero, and whether a year is a leap
year is the plain rule stated directly. It is proleptic
Gregorian throughout, applying today's calendar backward past
its historical adoption, which is stated because a date before
the sixteenth century computed here will not match a historical
record that used the Julian calendar then, and a caller
reasoning about old dates needs to know which calendar the
numbers assume. There are no times or time zones, only dates,
because a date is a day and the arithmetic of days is what this
is for.
"""

from __future__ import annotations

from loom.errors import Invalid

Date = tuple[int, int, int]


def is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _days_in_month(year: int, month: int) -> int:
    if month == 2:
        return 29 if is_leap(year) else 28
    return 31 if month in (1, 3, 5, 7, 8, 10, 12) else 30


def day_number(year: int, month: int, day: int) -> int:
    if not 1 <= month <= 12 or not 1 <= day <= _days_in_month(year, month):
        raise Invalid(f"{year}-{month}-{day} is not a valid date")
    y = year - (month <= 2)
    era = (y if y >= 0 else y - 399) // 400
    year_of_era = y - era * 400
    day_of_year = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
    day_of_era = (
        year_of_era * 365
        + year_of_era // 4
        - year_of_era // 100
        + day_of_year
    )
    return era * 146097 + day_of_era - 719468


def from_day_number(number: int) -> Date:
    z = number + 719468
    era = (z if z >= 0 else z - 146096) // 146097
    day_of_era = z - era * 146097
    year_of_era = (
        day_of_era
        - day_of_era // 1460
        + day_of_era // 36524
        - day_of_era // 146096
    ) // 365
    year = year_of_era + era * 400
    day_of_year = day_of_era - (
        365 * year_of_era + year_of_era // 4 - year_of_era // 100
    )
    month_position = (5 * day_of_year + 2) // 153
    day = day_of_year - (153 * month_position + 2) // 5 + 1
    month = month_position + (3 if month_position < 10 else -9)
    return (year + (month <= 2), month, day)


def days_between(start: Date, end: Date) -> int:
    return day_number(*end) - day_number(*start)


def add_days(date: Date, days: int) -> Date:
    return from_day_number(day_number(*date) + days)


def weekday(year: int, month: int, day: int) -> int:
    return (day_number(year, month, day) + 3) % 7
