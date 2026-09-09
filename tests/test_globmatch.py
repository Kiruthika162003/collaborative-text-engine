from __future__ import annotations

from loom.globmatch import matches


class TestStar:
    def test_star_matches_a_suffix(self):
        assert matches("*.txt", "file.txt")
        assert not matches("*.txt", "file.md")

    def test_star_matches_empty(self):
        assert matches("a*", "a")

    def test_star_matches_everything(self):
        assert matches("*", "anything at all")


class TestQuestion:
    def test_question_matches_one_char(self):
        assert matches("a?c", "abc")
        assert not matches("a?c", "ac")


class TestClass:
    def test_a_set_class(self):
        assert matches("[abc]at", "bat")
        assert not matches("[abc]at", "dat")

    def test_a_range_class(self):
        assert matches("[a-z]", "m")
        assert not matches("[a-z]", "5")

    def test_a_negated_class(self):
        assert matches("[!0-9]", "a")
        assert not matches("[!0-9]", "5")

    def test_a_caret_negation(self):
        assert matches("[^x]", "y")


class TestWhole:
    def test_a_pattern_must_match_the_whole_string(self):
        assert not matches("abc", "abcd")

    def test_empty_matches_empty(self):
        assert matches("", "")
