from __future__ import annotations

from loom.trie import Trie


def loaded() -> Trie:
    trie = Trie()
    for word in ["cat", "car", "cart", "dog"]:
        trie.insert(word)
    return trie


class TestContains:
    def test_an_inserted_word_is_found(self):
        assert loaded().contains("cat")

    def test_a_prefix_is_not_a_word(self):
        assert not loaded().contains("ca")

    def test_a_word_ending_where_another_continues(self):
        trie = loaded()
        assert trie.contains("car")
        assert trie.contains("cart")


class TestPrefix:
    def test_starts_with_finds_a_prefix(self):
        assert loaded().starts_with("ca")
        assert not loaded().starts_with("zz")

    def test_words_with_prefix_are_sorted(self):
        assert loaded().words_with_prefix("ca") == ["car", "cart", "cat"]

    def test_an_absent_prefix_has_no_words(self):
        assert loaded().words_with_prefix("zz") == []


class TestSize:
    def test_the_size_counts_distinct_words(self):
        assert len(loaded()) == 4

    def test_a_duplicate_insert_does_not_inflate(self):
        trie = Trie()
        trie.insert("x")
        trie.insert("x")
        assert len(trie) == 1
