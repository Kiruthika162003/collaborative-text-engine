from __future__ import annotations

from loom.hexdump import dump, hex_only


class TestDump:
    def test_a_short_row(self):
        line = dump(b"Hello")
        assert line.startswith("00000000  48 65 6c 6c 6f")
        assert line.endswith("|Hello|")

    def test_unprintable_bytes_are_dots(self):
        line = dump(b"\x00\x01A")
        assert line.endswith("|..A|")

    def test_multiple_rows(self):
        out = dump(bytes(range(20)))
        assert len(out.splitlines()) == 2
        assert out.splitlines()[1].startswith("00000010")

    def test_empty_data_is_empty(self):
        assert dump(b"") == ""


class TestHexOnly:
    def test_just_the_hex(self):
        assert hex_only(b"AB") == "41 42"

    def test_wraps_at_width(self):
        assert len(hex_only(bytes(range(20)), width=16).splitlines()) == 2
