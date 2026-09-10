from __future__ import annotations

import re

import pytest

from loom.errors import Invalid
from loom.regexlite import Regex


class TestFullMatch:
    def test_plain_literals(self):
        assert Regex("abc").fullmatch("abc")
        assert not Regex("abc").fullmatch("abd")
        assert not Regex("abc").fullmatch("ab")

    def test_the_wildcard_dot(self):
        assert Regex("a.c").fullmatch("axc")
        assert not Regex("a.c").fullmatch("ac")

    def test_star(self):
        pattern = Regex("ab*c")
        assert pattern.fullmatch("ac")
        assert pattern.fullmatch("abc")
        assert pattern.fullmatch("abbbbc")
        assert not pattern.fullmatch("abbd")

    def test_plus(self):
        pattern = Regex("ab+c")
        assert not pattern.fullmatch("ac")
        assert pattern.fullmatch("abc")
        assert pattern.fullmatch("abbc")

    def test_optional(self):
        pattern = Regex("colou?r")
        assert pattern.fullmatch("color")
        assert pattern.fullmatch("colour")
        assert not pattern.fullmatch("colouur")

    def test_alternation_and_groups(self):
        pattern = Regex("(cat|dog)s?")
        assert pattern.fullmatch("cat")
        assert pattern.fullmatch("cats")
        assert pattern.fullmatch("dog")
        assert not pattern.fullmatch("fish")

    def test_the_empty_pattern(self):
        assert Regex("").fullmatch("")
        assert not Regex("").fullmatch("a")

    def test_an_escaped_metacharacter(self):
        assert Regex(r"a\.b").fullmatch("a.b")
        assert not Regex(r"a\.b").fullmatch("axb")


class TestSearch:
    def test_search_finds_a_substring_match(self):
        assert Regex("b+").search("aaabbbccc")
        assert not Regex("z+").search("aaabbbccc")

    def test_search_finds_an_alternation(self):
        assert Regex("(quick|slow)").search("the quick brown fox")
        assert not Regex("(quick|slow)").search("the brown fox")


class TestNoCatastrophicBacktracking:
    def test_the_pathological_pattern_stays_fast(self):
        # (a*)* against a long run of a's followed by a mismatch is the
        # classic case that fells backtracking engines; Thompson is flat.
        pattern = Regex("(a*)*b")
        text = "a" * 40
        assert not pattern.fullmatch(text)
        assert pattern.fullmatch(text + "b")


class TestAgainstStdlib:
    def test_matches_the_re_module_on_a_battery(self):
        cases = [
            ("a.c", "abc"),
            ("a.c", "abd"),
            ("ab*c", "abbbbc"),
            ("ab*c", "abbd"),
            ("(cat|dog)s?", "cats"),
            ("(cat|dog)s?", "cows"),
            ("colou?r", "colour"),
            ("(ab)+", "ababab"),
            ("(ab)+", "aba"),
        ]
        for pattern, text in cases:
            expected = re.fullmatch(pattern, text) is not None
            assert Regex(pattern).fullmatch(text) == expected


class TestMalformed:
    def test_unmatched_parenthesis(self):
        with pytest.raises(Invalid):
            Regex("(ab")

    def test_a_stray_closing_parenthesis(self):
        with pytest.raises(Invalid):
            Regex("ab)")

    def test_a_dangling_escape(self):
        with pytest.raises(Invalid):
            Regex("ab\\")

    def test_a_leading_quantifier(self):
        with pytest.raises(Invalid):
            Regex("*ab")
