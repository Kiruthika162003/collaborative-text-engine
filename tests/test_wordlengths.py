from __future__ import annotations

from loom.author import Author
from loom.wordlengths import distribution, histogram, median_length, mode_length


def sample() -> Author:
    author = Author(site="alice")
    author.type_at(0, "a bb bb ccc dddd")
    return author


class TestDistribution:
    def test_lengths_are_counted(self):
        assert distribution(sample().weave) == {1: 1, 2: 2, 3: 1, 4: 1}

    def test_an_empty_document_distributes_nothing(self):
        author = Author(site="alice")
        assert distribution(author.weave) == {}


class TestDerived:
    def test_the_mode_is_the_most_common_length(self):
        assert mode_length(sample().weave) == 2

    def test_the_median_of_an_odd_count(self):
        author = Author(site="alice")
        author.type_at(0, "a bb ccc")
        assert median_length(author.weave) == 2.0

    def test_the_median_of_an_even_count(self):
        author = Author(site="alice")
        author.type_at(0, "a bb ccc dddd")
        assert median_length(author.weave) == 2.5

    def test_an_empty_document_has_zero_median(self):
        author = Author(site="alice")
        assert median_length(author.weave) == 0.0


class TestHistogram:
    def test_the_histogram_has_a_row_per_length(self):
        page = histogram(sample().weave)
        assert len(page.splitlines()) == 4

    def test_an_empty_document_has_no_histogram(self):
        author = Author(site="alice")
        assert "no words" in histogram(author.weave)
