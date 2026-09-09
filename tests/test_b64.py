from __future__ import annotations

import pytest

from loom.b64 import decode, encode
from loom.errors import Invalid


class TestEncode:
    def test_a_full_group(self):
        assert encode(b"Man") == "TWFu"

    def test_a_two_byte_tail_pads_once(self):
        assert encode(b"Ma") == "TWE="

    def test_a_one_byte_tail_pads_twice(self):
        assert encode(b"M") == "TQ=="

    def test_empty_is_empty(self):
        assert encode(b"") == ""


class TestDecode:
    def test_a_full_group(self):
        assert decode("TWFu") == b"Man"

    def test_padded_groups(self):
        assert decode("TWE=") == b"Ma"
        assert decode("TQ==") == b"M"

    def test_whitespace_is_ignored(self):
        assert decode("TW\nFu") == b"Man"

    def test_an_invalid_character_is_refused(self):
        with pytest.raises(Invalid):
            decode("TW*u")


class TestRoundTrip:
    def test_encode_then_decode_is_identity(self):
        for data in [b"", b"a", b"ab", b"abc", b"hello world", bytes(range(30))]:
            assert decode(encode(data)) == data
