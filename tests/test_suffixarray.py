from __future__ import annotations

from loom.suffixarray import SuffixArray, lcp_array, suffix_array


class TestOrder:
    def test_banana(self):
        # Sorted suffixes of "banana": a, ana, anana, banana, na, nana
        assert suffix_array("banana") == [5, 3, 1, 0, 4, 2]

    def test_the_empty_text(self):
        assert suffix_array("") == []

    def test_the_order_is_the_sorted_suffixes(self):
        text = "mississippi"
        order = suffix_array(text)
        suffixes = [text[i:] for i in order]
        assert suffixes == sorted(text[i:] for i in range(len(text)))


class TestLcp:
    def test_banana_overlaps(self):
        text = "banana"
        order = suffix_array(text)
        # neighbour overlaps: a|ana=1, ana|anana=3, anana|banana=0, banana|na=0, na|nana=2
        assert lcp_array(text, order) == [0, 1, 3, 0, 0, 2]


class TestSearch:
    def test_finds_all_occurrences(self):
        index = SuffixArray("mississippi")
        assert index.search("issi") == [1, 4]
        assert index.search("s") == [2, 3, 5, 6]
        assert index.count("i") == 4

    def test_a_missing_pattern(self):
        index = SuffixArray("mississippi")
        assert index.search("xyz") == []
        assert not index.contains("abc")

    def test_agrees_with_str_find_style_scan(self):
        text = "the quick brown fox the quick"
        index = SuffixArray(text)
        for pattern in ("the", "quick", "o", "z", "the quick"):
            expected = [i for i in range(len(text)) if text.startswith(pattern, i)]
            assert index.search(pattern) == expected


class TestLongestRepeat:
    def test_the_longest_repeated_substring(self):
        assert SuffixArray("banana").longest_repeated_substring() == "ana"

    def test_a_repeated_phrase(self):
        text = "the quick brown fox the quick"
        assert SuffixArray(text).longest_repeated_substring() == "the quick"

    def test_no_repeat(self):
        assert SuffixArray("abcd").longest_repeated_substring() == ""
