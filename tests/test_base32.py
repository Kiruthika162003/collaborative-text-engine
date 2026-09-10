from __future__ import annotations

import base64
import random

import pytest

from loom.base32 import decode, encode
from loom.errors import Invalid


class TestAgainstStdlib:
    def test_known_vectors(self):
        # RFC 4648 test vectors.
        assert encode(b"") == ""
        assert encode(b"f") == "MY======"
        assert encode(b"fo") == "MZXQ===="
        assert encode(b"foo") == "MZXW6==="
        assert encode(b"foob") == "MZXW6YQ="
        assert encode(b"fooba") == "MZXW6YTB"
        assert encode(b"foobar") == "MZXW6YTBOI======"

    def test_encode_matches_the_library(self):
        rng = random.Random(3)
        for _ in range(300):
            data = bytes(rng.randrange(256) for _ in range(rng.randint(0, 20)))
            assert encode(data) == base64.b32encode(data).decode("ascii")


class TestRoundTrip:
    def test_decode_undoes_encode(self):
        rng = random.Random(4)
        for _ in range(300):
            data = bytes(rng.randrange(256) for _ in range(rng.randint(0, 20)))
            assert decode(encode(data)) == data

    def test_decode_matches_the_library(self):
        rng = random.Random(5)
        for _ in range(200):
            data = bytes(rng.randrange(256) for _ in range(rng.randint(1, 20)))
            text = base64.b32encode(data).decode("ascii")
            assert decode(text) == data


class TestGuards:
    def test_a_character_outside_the_alphabet_is_refused(self):
        with pytest.raises(Invalid):
            decode("MZXW6!==")
