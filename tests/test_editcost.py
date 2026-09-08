from __future__ import annotations

from loom.editcost import distance, similarity, sync_lower_bound


class TestDistance:
    def test_identical_costs_nothing(self):
        assert distance("same", "same") == 0

    def test_one_substitution(self):
        assert distance("cat", "cut") == 1

    def test_one_insertion_and_deletion(self):
        assert distance("cat", "cats") == 1
        assert distance("cats", "cat") == 1

    def test_the_classic_example(self):
        assert distance("kitten", "sitting") == 3

    def test_empty_costs_the_other_length(self):
        assert distance("", "hello") == 5
        assert distance("hello", "") == 5


class TestSimilarity:
    def test_identical_texts_are_wholly_similar(self):
        assert similarity("draft", "draft") == 1.0
        assert similarity("", "") == 1.0

    def test_a_near_edit_sorts_above_a_rewrite(self):
        near = similarity("hello world", "hello worle")
        far = similarity("hello world", "zzzzz zzzzz")
        assert near > far

    def test_similarity_stays_in_the_unit_interval(self):
        for a, b in [
            ("abc", "xyz"),
            ("a", "abcdef"),
            ("same", "same"),
        ]:
            assert 0.0 <= similarity(a, b) <= 1.0


class TestLowerBound:
    def test_the_bound_names_the_operations(self):
        message = sync_lower_bound("cat", "dog")
        assert "at least 3 operation(s)" in message
        assert "what a scheduler wants" in message
