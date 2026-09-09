from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.huffman import Huffman


class TestRoundTrip:
    def test_encode_then_decode_returns_the_text(self):
        text = "the quick brown fox jumps over the lazy dog"
        code = Huffman.from_data(text)
        assert code.decode(code.encode(text)) == text

    def test_a_single_repeated_symbol(self):
        code = Huffman.from_data("aaaa")
        assert code.table == {"a": "0"}
        assert code.encode("aaaa") == "0000"
        assert code.decode("0000") == "aaaa"

    def test_two_symbols_get_one_bit_each(self):
        code = Huffman.from_data("abab")
        assert set(code.table.values()) == {"0", "1"}
        assert code.decode(code.encode("abba")) == "abba"


class TestPrefixFree:
    def test_no_code_is_a_prefix_of_another(self):
        code = Huffman.from_data("mississippi river")
        codes = list(code.table.values())
        for i, one in enumerate(codes):
            for j, other in enumerate(codes):
                if i != j:
                    assert not other.startswith(one)


class TestShorterThanFixedWidth:
    def test_skewed_text_beats_fixed_width(self):
        # Heavily skewed: one symbol dominates.
        text = "a" * 100 + "b" * 10 + "c" * 3 + "d"
        code = Huffman.from_data(text)
        fixed_width_bits = len(text) * 2  # four symbols need two bits each
        assert code.encoded_length(text) < fixed_width_bits

    def test_the_common_symbol_gets_the_shorter_code(self):
        text = "a" * 100 + "b" * 10 + "c" * 3 + "d"
        code = Huffman.from_data(text)
        assert len(code.table["a"]) <= len(code.table["d"])


class TestDeterminism:
    def test_the_same_text_builds_the_same_table(self):
        text = "collaboration converges"
        assert Huffman.from_data(text).table == Huffman.from_data(text).table


class TestGuards:
    def test_building_from_empty_is_refused(self):
        with pytest.raises(Invalid):
            Huffman.from_data("")

    def test_trailing_bits_that_complete_nothing_are_refused(self):
        # a:3 sits at depth one with a one-bit code; b and c share the
        # other first bit as two-bit codes, so that lone bit spells nothing.
        code = Huffman.from_data("aaabbc")
        one_bit = next(bits for bits in code.table.values() if len(bits) == 1)
        dangling = "1" if one_bit == "0" else "0"
        with pytest.raises(Invalid):
            code.decode(dangling)

    def test_encoding_an_unknown_symbol_is_refused(self):
        code = Huffman.from_data("abab")
        with pytest.raises(Invalid):
            code.encode("z")
