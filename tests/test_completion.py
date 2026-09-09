from __future__ import annotations

import pytest

from loom.author import Author
from loom.completion import complete, ranked, vocabulary_size
from loom.errors import Invalid


class TestComplete:
    def test_a_prefix_finds_matching_words(self):
        author = Author(site="alice")
        author.type_at(0, "repository repose repel other")
        assert complete(author.weave, "rep") == [
            "repel",
            "repose",
            "repository",
        ]

    def test_more_frequent_words_rank_higher(self):
        author = Author(site="alice")
        author.type_at(0, "test test testing tent")
        assert complete(author.weave, "te")[0] == "test"

    def test_the_prefix_itself_is_not_offered(self):
        author = Author(site="alice")
        author.type_at(0, "plan plans planning")
        assert "plan" not in complete(author.weave, "plan")

    def test_case_folds_and_offers_the_common_form(self):
        author = Author(site="alice")
        author.type_at(0, "Loom loom loom LOOM weaving")
        assert complete(author.weave, "lo") == ["loom"]

    def test_an_empty_prefix_is_refused(self):
        author = Author(site="alice")
        author.type_at(0, "words here")
        with pytest.raises(Invalid):
            complete(author.weave, "")


class TestRanked:
    def test_ranked_carries_counts(self):
        author = Author(site="alice")
        author.type_at(0, "code code coder")
        assert ranked(author.weave, "cod") == [("code", 2), ("coder", 1)]

    def test_a_prefix_matching_nothing_is_empty(self):
        author = Author(site="alice")
        author.type_at(0, "alpha beta")
        assert ranked(author.weave, "zz") == []


class TestVocabulary:
    def test_vocabulary_size_folds_case(self):
        author = Author(site="alice")
        author.type_at(0, "The the THE cat")
        assert vocabulary_size(author.weave) == 2

    def test_a_limit_caps_the_suggestions(self):
        author = Author(site="alice")
        author.type_at(0, "aa ab ac ad ae af")
        assert len(complete(author.weave, "a", limit=3)) == 3
