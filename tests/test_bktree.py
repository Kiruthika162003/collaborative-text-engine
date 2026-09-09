from __future__ import annotations

from loom.bktree import BKTree, of_words
from loom.didyoumean import nearest


class TestFind:
    def test_near_words_are_found(self):
        tree = of_words(["cat", "car", "cot", "dog", "cart"])
        found = {word for word, _d in tree.find("cat", 1)}
        # cart is distance one from cat, an inserted r
        assert found == {"cat", "car", "cot", "cart"}

    def test_results_are_nearest_first(self):
        tree = of_words(["cat", "car", "cart"])
        result = tree.find("cat", 2)
        assert result[0] == ("cat", 0)

    def test_exact_search_finds_only_the_word(self):
        tree = of_words(["cat", "car"])
        assert tree.find("cat", 0) == [("cat", 0)]

    def test_an_empty_tree_finds_nothing(self):
        assert BKTree().find("cat", 3) == []


class TestBuild:
    def test_size_counts_distinct_words(self):
        tree = of_words(["a", "b", "a"])
        assert len(tree) == 2


class TestAgreement:
    def test_it_agrees_with_the_linear_scanner(self):
        words = ["cat", "car", "cot", "cart", "dog", "cog"]
        tree = of_words(words)
        by_tree = {word for word, _d in tree.find("cat", 2)}
        by_scan = {word for word, _d in nearest("cat", set(words), limit=99, max_distance=2)}
        by_scan.add("cat")
        assert by_tree == by_scan
