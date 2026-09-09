from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.lzw import compress, decompress


class TestRoundTrip:
    def test_ordinary_text(self):
        text = "the quick brown fox jumps over the lazy dog"
        alphabet, codes = compress(text)
        assert decompress(alphabet, codes) == text

    def test_the_empty_string(self):
        alphabet, codes = compress("")
        assert codes == []
        assert decompress(alphabet, codes) == ""

    def test_a_single_symbol_run(self):
        text = "aaaaaaaa"
        alphabet, codes = compress(text)
        assert decompress(alphabet, codes) == text

    def test_the_immediate_repeat_special_case(self):
        # ababab... is the pattern that makes the encoder emit a code
        # the decoder has not added yet.
        text = "ababababababab"
        alphabet, codes = compress(text)
        assert decompress(alphabet, codes) == text

    def test_repeated_words(self):
        text = "go go gophers go go gophers"
        alphabet, codes = compress(text)
        assert decompress(alphabet, codes) == text


class TestCompression:
    def test_repetition_shrinks_the_code_count(self):
        text = "abcabcabcabcabcabcabcabc"
        _, codes = compress(text)
        assert len(codes) < len(text)

    def test_the_dictionary_learns_reused_runs(self):
        # Second half repeats the first, so its codes are fewer.
        text = "abcdefabcdef"
        _, codes = compress(text)
        assert len(codes) < len(text)


class TestGuards:
    def test_a_code_from_the_future_is_refused(self):
        with pytest.raises(Invalid):
            decompress("ab", [0, 99])

    def test_a_first_code_outside_the_alphabet_is_refused(self):
        with pytest.raises(Invalid):
            decompress("ab", [5])
