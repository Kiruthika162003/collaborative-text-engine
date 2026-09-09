from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.phrases import frequencies, ngrams, repeated, report


class TestNgrams:
    def test_bigrams_are_consecutive_pairs(self):
        assert ngrams("a b c", 2) == [("a", "b"), ("b", "c")]

    def test_trigrams_are_triples(self):
        assert ngrams("a b c d", 3) == [("a", "b", "c"), ("b", "c", "d")]

    def test_a_zero_gram_is_refused(self):
        with pytest.raises(Invalid):
            ngrams("a b", 0)


class TestFrequencies:
    def test_a_repeated_bigram_is_counted(self):
        counts = frequencies("the cat sat the cat ran", 2)
        assert counts["the cat"] == 2

    def test_case_is_folded(self):
        counts = frequencies("Big Deal big deal", 2)
        assert counts["big deal"] == 2


class TestRepeated:
    def test_only_repeats_are_reported(self):
        assert repeated("the cat sat the cat ran", 2) == [("the cat", 2)]

    def test_a_document_without_repeats_is_empty(self):
        assert repeated("all unique words here", 2) == []

    def test_ranking_is_by_count_then_phrase(self):
        text = "x y x y a b a b a b"
        top = repeated(text, 2)[0]
        assert top == ("a b", 3)


class TestReport:
    def test_the_report_lists_repeats(self):
        page = report("go now go now", 2)
        assert "'go now' (2)" in page

    def test_no_repeats_says_so(self):
        assert "no 2-word phrase repeats" in report("a b c", 2)
