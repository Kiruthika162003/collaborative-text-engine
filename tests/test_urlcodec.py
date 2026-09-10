from __future__ import annotations

import random
import string
import urllib.parse

import pytest

from loom.errors import Invalid
from loom.urlcodec import quote, unquote


class TestQuote:
    def test_safe_characters_pass_through(self):
        assert quote("abcXYZ012-._~") == "abcXYZ012-._~"

    def test_a_space_and_punctuation_are_encoded(self):
        assert quote("a b/c") == "a%20b%2Fc"

    def test_non_ascii_encodes_each_byte(self):
        # e-acute is two UTF-8 bytes, so two percent groups.
        assert quote("é") == "%C3%A9"

    def test_matches_the_library(self):
        rng = random.Random(37)
        pool = string.printable + "éüñ你好"
        for _ in range(300):
            text = "".join(rng.choice(pool) for _ in range(rng.randint(0, 20)))
            assert quote(text) == urllib.parse.quote(text, safe="")


class TestUnquote:
    def test_round_trip(self):
        rng = random.Random(41)
        pool = string.printable + "éüñ你好"
        for _ in range(300):
            text = "".join(rng.choice(pool) for _ in range(rng.randint(0, 20)))
            assert unquote(quote(text)) == text

    def test_matches_the_library(self):
        assert unquote("a%20b%2Fc") == urllib.parse.unquote("a%20b%2Fc")

    def test_a_malformed_group_is_refused(self):
        with pytest.raises(Invalid):
            unquote("a%2")

    def test_a_non_hex_group_is_refused(self):
        with pytest.raises(Invalid):
            unquote("a%zz")


class TestSafe:
    def test_extra_safe_characters_are_kept(self):
        assert quote("a/b", safe="/") == "a/b"
