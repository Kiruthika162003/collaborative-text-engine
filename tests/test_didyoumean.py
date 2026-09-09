from __future__ import annotations

from loom.author import Author
from loom.didyoumean import did_you_mean, nearest, suggest


class TestNearest:
    def test_near_words_are_ranked_by_distance(self):
        result = nearest("cat", {"car", "cot", "cats", "dog"})
        assert ("dog", 3) not in result
        assert {word for word, _d in result} == {"car", "cot", "cats"}

    def test_ties_break_alphabetically(self):
        result = nearest("cat", {"car", "cot", "cats", "dog"})
        assert [word for word, _d in result] == ["car", "cats", "cot"]

    def test_a_far_word_is_excluded(self):
        assert nearest("cat", {"elephant"}) == []

    def test_the_word_itself_is_not_suggested(self):
        assert nearest("cat", {"cat", "car"}) == [("car", 1)]


class TestDidYouMean:
    def test_the_single_best_is_returned(self):
        assert did_you_mean("colour", {"color", "flavour"}) == "color"

    def test_nothing_close_returns_none(self):
        assert did_you_mean("xyz", {"elephant"}) is None


class TestSuggest:
    def test_suggestions_come_from_the_document(self):
        author = Author(site="alice")
        author.type_at(0, "the theme is set")
        result = suggest(author.weave, "hte")
        assert "the" in {word for word, _d in result}
