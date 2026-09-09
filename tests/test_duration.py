from __future__ import annotations

import pytest

from loom.duration import brief, format_duration, parse_duration
from loom.errors import Invalid


class TestFormat:
    def test_a_full_breakdown(self):
        assert format_duration(3723) == "1h 2m 3s"

    def test_zero_units_are_omitted(self):
        assert format_duration(3600) == "1h"

    def test_days_are_the_largest_unit(self):
        assert format_duration(90000) == "1d 1h"

    def test_zero_is_zero_seconds(self):
        assert format_duration(0) == "0s"

    def test_a_negative_span_is_refused(self):
        with pytest.raises(Invalid):
            format_duration(-1)


class TestParse:
    def test_a_string_parses_to_seconds(self):
        assert parse_duration("1h30m") == 5400

    def test_spaces_are_tolerated(self):
        assert parse_duration("2h 15m") == 8100

    def test_a_unitless_string_is_refused(self):
        with pytest.raises(Invalid):
            parse_duration("hello")


class TestRoundTrip:
    def test_format_then_parse_is_identity(self):
        for seconds in [0, 59, 60, 3723, 90000, 100000]:
            assert parse_duration(format_duration(seconds) or "0s") == seconds


class TestBrief:
    def test_brief_gives_the_largest_unit(self):
        assert brief(3723) == "1h"
        assert brief(90000) == "1d"
