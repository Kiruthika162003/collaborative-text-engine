from __future__ import annotations

import random

from loom.horspool import contains, first, search
from loom.kmp import search as kmp_search


class TestSearch:
    def test_finds_every_occurrence(self):
        assert search("abababab", "ab") == [0, 2, 4, 6]

    def test_finds_overlapping_occurrences(self):
        assert search("aaaa", "aa") == [0, 1, 2]

    def test_no_match(self):
        assert search("abcdef", "xyz") == []

    def test_a_match_at_the_end(self):
        assert search("hello world", "world") == [6]

    def test_a_pattern_longer_than_text(self):
        assert search("hi", "hello") == []

    def test_the_empty_pattern(self):
        assert search("abc", "") == [0, 1, 2, 3]


class TestConvenience:
    def test_first_matches_str_find(self):
        for text, pattern in [("mississippi", "sip"), ("abc", "z"), ("abc", "c")]:
            assert first(text, pattern) == text.find(pattern)

    def test_contains(self):
        assert contains("mississippi", "ssi")
        assert not contains("mississippi", "xyz")


class TestAgreesWithKmp:
    def test_the_two_searches_agree_on_a_battery(self):
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

    def test_agreement_over_random_inputs(self):
        rng = random.Random(3)
        alphabet = "abc"
        for _ in range(300):
            text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 30)))
            pattern = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 5)))
            assert search(text, pattern) == kmp_search(text, pattern)
