from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.hexcolor import is_dark, luminance, parse, to_hex


class TestParse:
    def test_a_long_form(self):
        assert parse("#ff0000") == (255, 0, 0)

    def test_a_short_form_expands(self):
        assert parse("#fff") == (255, 255, 255)

    def test_the_hash_is_optional(self):
        assert parse("00ff00") == (0, 255, 0)

    def test_a_bad_color_is_refused(self):
        with pytest.raises(Invalid):
            parse("#xyz")


class TestRender:
    def test_to_hex(self):
        assert to_hex(255, 0, 0) == "#ff0000"

    def test_round_trip(self):
        assert to_hex(*parse("#123456")) == "#123456"


class TestLightness:
    def test_white_is_brighter_than_black(self):
        assert luminance(255, 255, 255) > luminance(0, 0, 0)

    def test_green_outweighs_blue(self):
        assert luminance(0, 255, 0) > luminance(0, 0, 255)

    def test_is_dark(self):
        assert is_dark("#000000")
        assert not is_dark("#ffffff")

    def test_a_custom_threshold(self):
        assert is_dark("#888888", threshold=200)
