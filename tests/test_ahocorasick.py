from __future__ import annotations

from loom.ahocorasick import AhoCorasick


class TestSearch:
    def test_finds_several_patterns_in_one_pass(self):
        automaton = AhoCorasick(["he", "she", "his", "hers"])
        assert automaton.search("ushers") == [(1, "she"), (2, "he"), (2, "hers")]

    def test_overlapping_and_nested_patterns(self):
        automaton = AhoCorasick(["a", "ab", "bab", "bc", "bca", "c", "caa"])
        found = automaton.search("abccab")
        assert (0, "a") in found
        assert (0, "ab") in found
        assert (2, "c") in found
        assert (3, "c") in found

    def test_a_pattern_that_does_not_occur(self):
        automaton = AhoCorasick(["cat", "dog"])
        assert automaton.search("the bird flew") == []

    def test_repeated_matches(self):
        automaton = AhoCorasick(["ab"])
        assert automaton.search("abab") == [(0, "ab"), (2, "ab")]


class TestConvenience:
    def test_contains_any(self):
        automaton = AhoCorasick(["forbidden", "banned"])
        assert automaton.contains_any("this is forbidden text")
        assert not automaton.contains_any("this is fine")

    def test_count(self):
        automaton = AhoCorasick(["is", "the"])
        assert automaton.count("this is the thesis") == 5


class TestAgainstNaiveMultiSearch:
    def test_matches_a_loop_of_single_pattern_scans(self):
        patterns = ["the", "he", "her", "e", "there", "here"]
        text = "there is another heron over there"
        automaton = AhoCorasick(patterns)
        expected = sorted(
            (i, pattern)
            for pattern in patterns
            for i in range(len(text))
            if text.startswith(pattern, i)
        )
        assert automaton.search(text) == expected


class TestEdgeCases:
    def test_empty_patterns_are_ignored(self):
        automaton = AhoCorasick(["", "ab", ""])
        assert automaton.search("zabz") == [(1, "ab")]

    def test_no_patterns_finds_nothing(self):
        assert AhoCorasick([]).search("anything") == []
