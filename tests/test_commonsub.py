from __future__ import annotations

from loom.commonsub import (
    lcs_length,
    longest_common_subsequence,
    longest_common_substring,
)


class TestSubstring:
    def test_a_shared_run_is_found(self):
        assert longest_common_substring("abcdef", "zzabcyy") == "abc"

    def test_a_shared_phrase_including_space(self):
        assert longest_common_substring(
            "hello world", "goodbye world"
        ) == " world"

    def test_no_overlap_is_empty(self):
        assert longest_common_substring("abc", "xyz") == ""

    def test_an_empty_input_is_empty(self):
        assert longest_common_substring("", "abc") == ""


class TestSubsequence:
    def test_a_shared_subsequence_is_found(self):
        assert longest_common_subsequence("abcde", "ace") == "ace"

    def test_a_scattered_subsequence(self):
        assert longest_common_subsequence("axbxcx", "abc") == "abc"

    def test_lcs_length_counts(self):
        assert lcs_length("abcde", "ace") == 3

    def test_no_common_subsequence_is_empty(self):
        assert longest_common_subsequence("abc", "xyz") == ""
