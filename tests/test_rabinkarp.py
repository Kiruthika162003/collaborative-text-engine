from __future__ import annotations

from loom.kmp import search as kmp_search
from loom.rabinkarp import contains, first, rolling_hash, search


class TestRollingHash:
    def test_equal_strings_hash_equal(self):
        assert rolling_hash("hello") == rolling_hash("hello")

    def test_different_strings_usually_differ(self):
        assert rolling_hash("hello") != rolling_hash("world")


class TestSearch:
    def test_finds_every_occurrence(self):
        assert search("abababab", "ab") == [0, 2, 4, 6]

    def test_finds_overlapping_occurrences(self):
        assert search("aaaa", "aa") == [0, 1, 2]

    def test_no_match_is_empty(self):
        assert search("abcdef", "xyz") == []

    def test_a_pattern_longer_than_the_text(self):
        assert search("hi", "hello") == []

    def test_the_empty_pattern_matches_everywhere(self):
        assert search("abc", "") == [0, 1, 2, 3]


class TestAgreesWithKmp:
    def test_the_two_searches_agree(self):
        cases = [
            ("mississippi", "issi"),
            ("the quick brown fox", "o"),
            ("aaaaaa", "aaa"),
            ("abcabcabc", "abc"),
            ("hello world", "xyz"),
            ("edge", "edge"),
        ]
        for text, pattern in cases:
            assert search(text, pattern) == kmp_search(text, pattern)


class TestConvenience:
    def test_first_matches_str_find(self):
        for text, pattern in [("mississippi", "sip"), ("abc", "z"), ("abc", "c")]:
            assert first(text, pattern) == text.find(pattern)

    def test_contains(self):
        assert contains("mississippi", "ssi")
        assert not contains("mississippi", "xyz")
