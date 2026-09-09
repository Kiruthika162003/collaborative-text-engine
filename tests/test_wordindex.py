from __future__ import annotations

from loom.author import Author
from loom.wordindex import WordIndex


def indexed() -> WordIndex:
    author = Author(site="alice")
    author.type_at(0, "the cat\nthe dog\nblue cat")
    return WordIndex.build(author.weave)


class TestLookup:
    def test_lines_for_a_word(self):
        assert indexed().lines_for("cat") == [0, 2]

    def test_case_is_folded(self):
        author = Author(site="alice")
        author.type_at(0, "The\nthe")
        assert WordIndex.build(author.weave).lines_for("the") == [0, 1]

    def test_frequency_counts_occurrences(self):
        assert indexed().frequency("the") == 2

    def test_contains(self):
        index = indexed()
        assert index.contains("dog")
        assert not index.contains("fish")


class TestMultiWord:
    def test_lines_with_all_words(self):
        assert indexed().lines_with_all(["cat", "blue"]) == [2]

    def test_no_common_line(self):
        assert indexed().lines_with_all(["dog", "blue"]) == []

    def test_empty_query_has_no_lines(self):
        assert indexed().lines_with_all([]) == []


class TestVocabulary:
    def test_vocabulary_is_sorted(self):
        assert indexed().vocabulary() == ["blue", "cat", "dog", "the"]

    def test_len_is_the_vocabulary_size(self):
        assert len(indexed()) == 4
