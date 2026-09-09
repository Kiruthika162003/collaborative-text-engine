from __future__ import annotations

from loom.kmp import contains, count, first, prefix_function, search


class TestPrefixFunction:
    def test_no_repeated_prefix(self):
        assert prefix_function("abcd") == [0, 0, 0, 0]

    def test_a_repeating_pattern(self):
        assert prefix_function("aabaa") == [0, 1, 0, 1, 2]

    def test_the_classic_ababaca(self):
        assert prefix_function("ababaca") == [0, 0, 1, 2, 3, 0, 1]


class TestSearch:
    def test_finds_every_occurrence(self):
        assert search("abababab", "ab") == [0, 2, 4, 6]

    def test_finds_overlapping_occurrences(self):
        assert search("aaaa", "aa") == [0, 1, 2]

    def test_no_match_is_empty(self):
        assert search("abcdef", "xyz") == []

    def test_a_match_at_the_very_end(self):
        assert search("hello world", "world") == [6]

    def test_the_empty_pattern_matches_everywhere(self):
        assert search("abc", "") == [0, 1, 2, 3]


class TestConvenience:
    def test_first_matches_str_find(self):
        cases = [
            ("hello world", "o"),
            ("hello world", "world"),
            ("hello world", "xyz"),
            ("mississippi", "issi"),
            ("abc", ""),
        ]
        for text, pattern in cases:
            assert first(text, pattern) == text.find(pattern)

    def test_contains_matches_the_in_operator(self):
        assert contains("mississippi", "sip")
        assert not contains("mississippi", "sea")

    def test_count_counts_overlapping_matches(self):
        assert count("aaaa", "aa") == 3
        assert count("abababab", "ab") == 4
