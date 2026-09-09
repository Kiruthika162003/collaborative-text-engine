from __future__ import annotations

from loom.worddelta import added, changed, net_words, removed


class TestDelta:
    def test_added_and_removed_words(self):
        assert added("the cat sat", "the dog sat") == {"dog": 1}
        assert removed("the cat sat", "the dog sat") == {"cat": 1}

    def test_counts_track_repetition(self):
        assert added("one the", "the the the") == {"the": 2}

    def test_case_is_folded(self):
        assert added("The", "the the") == {"the": 1}

    def test_a_reorder_changes_nothing(self):
        assert added("a b", "b a") == {}
        assert removed("a b", "b a") == {}


class TestNet:
    def test_net_words_counts_the_difference(self):
        assert net_words("a b", "a b c d") == 2
        assert net_words("a b c", "a") == -2


class TestChanged:
    def test_changed_ignores_order(self):
        assert not changed("a b c", "c b a")
        assert changed("a b", "a c")
