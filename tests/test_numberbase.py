from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.numberbase import from_base, to_base


class TestToBase:
    def test_hex_and_binary(self):
        assert to_base(255, 16) == "ff"
        assert to_base(10, 2) == "1010"

    def test_zero(self):
        assert to_base(0, 2) == "0"

    def test_a_negative_keeps_its_sign(self):
        assert to_base(-5, 2) == "-101"

    def test_a_bad_base_is_refused(self):
        with pytest.raises(Invalid):
            to_base(10, 1)


class TestFromBase:
    def test_reads_a_base(self):
        assert from_base("ff", 16) == 255
        assert from_base("1010", 2) == 10

    def test_case_is_folded(self):
        assert from_base("FF", 16) == 255

    def test_a_negative(self):
        assert from_base("-101", 2) == -5

    def test_a_bad_digit_is_refused(self):
        with pytest.raises(Invalid):
            from_base("2", 2)


class TestRoundTrip:
    def test_to_then_from_is_identity(self):
        for number in [0, 5, 255, 1000, -42]:
            for base in [2, 8, 16, 36]:
                assert from_base(to_base(number, base), base) == number
