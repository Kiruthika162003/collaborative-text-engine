from __future__ import annotations

import pytest

from loom.bitops import (
    clear_bit,
    is_power_of_two,
    lowest_set_bit,
    popcount,
    rotate_left,
    set_bit,
    toggle_bit,
)
from loom.bitops import test_bit as bit_is_set
from loom.errors import Invalid


class TestSingleBits:
    def test_set_clear_toggle_test(self):
        assert set_bit(0, 3) == 8
        assert clear_bit(0b1111, 1) == 0b1101
        assert toggle_bit(0, 0) == 1
        assert bit_is_set(0b100, 2)
        assert not bit_is_set(0b100, 1)


class TestCounts:
    def test_popcount(self):
        assert popcount(0b1011) == 3
        assert popcount(0) == 0

    def test_a_negative_popcount_is_refused(self):
        with pytest.raises(Invalid):
            popcount(-1)

    def test_power_of_two(self):
        assert is_power_of_two(8)
        assert not is_power_of_two(6)
        assert not is_power_of_two(0)

    def test_lowest_set_bit(self):
        assert lowest_set_bit(0b1100) == 2
        assert lowest_set_bit(0) == -1


class TestRotate:
    def test_rotation_wraps_within_the_width(self):
        assert rotate_left(0b1000, 1, 4) == 0b0001

    def test_a_full_rotation_returns_the_value(self):
        assert rotate_left(0b1010, 4, 4) == 0b1010

    def test_a_zero_width_is_refused(self):
        with pytest.raises(Invalid):
            rotate_left(1, 1, 0)
