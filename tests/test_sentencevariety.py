from __future__ import annotations

import math

import pytest

from loom.author import Author
from loom.sentencevariety import (
    mean_length,
    report,
    sentence_lengths,
    stddev_length,
    variance,
)


def sample() -> Author:
    author = Author(site="alice")
    author.type_at(0, "One. Two two. Three three three.")
    return author


class TestLengths:
    def test_lengths_are_word_counts_per_sentence(self):
        assert sentence_lengths(sample().weave) == [1, 2, 3]

    def test_an_empty_document_has_no_lengths(self):
        author = Author(site="alice")
        assert sentence_lengths(author.weave) == []


class TestStatistics:
    def test_the_mean_length(self):
        assert mean_length(sample().weave) == 2.0

    def test_the_variance(self):
        assert variance(sample().weave) == pytest.approx(2 / 3)

    def test_the_deviation(self):
        assert stddev_length(sample().weave) == pytest.approx(math.sqrt(2 / 3))

    def test_uniform_sentences_have_zero_deviation(self):
        author = Author(site="alice")
        author.type_at(0, "Two words. Two words.")
        assert stddev_length(author.weave) == 0.0


class TestReport:
    def test_the_report_disavows_a_verdict(self):
        assert "not a verdict" in report(sample().weave)

    def test_an_empty_document_reports_no_rhythm(self):
        author = Author(site="alice")
        assert "no rhythm" in report(author.weave)
