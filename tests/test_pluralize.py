from __future__ import annotations

from loom.pluralize import count_noun, pluralize


class TestRegular:
    def test_a_plain_s(self):
        assert pluralize("cat") == "cats"

    def test_a_sibilant_takes_es(self):
        assert pluralize("box") == "boxes"
        assert pluralize("bus") == "buses"
        assert pluralize("church") == "churches"

    def test_consonant_y_becomes_ies(self):
        assert pluralize("baby") == "babies"

    def test_a_vowel_y_takes_s(self):
        assert pluralize("day") == "days"

    def test_f_and_fe_become_ves(self):
        assert pluralize("leaf") == "leaves"
        assert pluralize("knife") == "knives"


class TestExceptions:
    def test_irregulars_from_the_table(self):
        assert pluralize("child") == "children"
        assert pluralize("person") == "people"

    def test_unchanged_words(self):
        assert pluralize("sheep") == "sheep"

    def test_case_is_carried(self):
        assert pluralize("Child") == "Children"


class TestCountNoun:
    def test_one_is_singular(self):
        assert count_noun(1, "cat") == "1 cat"

    def test_more_than_one_is_plural(self):
        assert count_noun(2, "cat") == "2 cats"

    def test_zero_is_plural(self):
        assert count_noun(0, "item") == "0 items"
