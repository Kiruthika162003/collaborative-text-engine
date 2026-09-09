from __future__ import annotations

import zlib

from loom.crc32 import crc32, hex_crc32


class TestCrc32:
    def test_empty_is_zero(self):
        assert crc32(b"") == 0

    def test_known_values(self):
        assert crc32(b"hello") == 0x3610A686
        assert hex_crc32(b"hello") == "3610a686"

    def test_it_matches_zlib(self):
        for data in [
            b"",
            b"a",
            b"hello world",
            b"The quick brown fox",
            bytes(range(60)),
        ]:
            assert crc32(data) == zlib.crc32(data)


class TestStreaming:
    def test_a_seed_continues_the_checksum(self):
        whole = crc32(b"helloworld")
        streamed = crc32(b"world", crc32(b"hello"))
        assert streamed == whole

    def test_the_seed_matches_zlib(self):
        seed = crc32(b"hello")
        assert crc32(b"world", seed) == zlib.crc32(b"world", zlib.crc32(b"hello"))
