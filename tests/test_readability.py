from __future__ import annotations

from loom.author import Author
from loom.readability import (
    flesch_kincaid_grade,
    flesch_reading_ease,
    report,
    sentence_count,
    syllable_total,
    syllables,
)


class TestSyllables:
    def test_the_rule_gets_queue_right(self):
        assert syllables("queue") == 1

    def test_the_rule_undercounts_area(self):
        # area is three syllables; the vowel-group rule
        # measures two, recorded rather than guessed
        assert syllables("area") == 2

    def test_the_rule_undercounts_simile(self):
        assert syllables("simile") == 2

    def test_a_silent_e_is_not_its_own_syllable(self):
        assert syllables("fire") == 1

    def test_a_wordless_token_has_no_syllables(self):
        assert syllables("123") == 0


class TestSentences:
    def test_terminal_punctuation_divides_sentences(self):
        author = Author(site="alice")
        author.type_at(0, "One thing. Then another! And a third?")
        assert sentence_count(author.weave) == 3

    def test_prose_without_punctuation_is_one_sentence(self):
        author = Author(site="alice")
        author.type_at(0, "just a run of words")
        assert sentence_count(author.weave) == 1

    def test_an_empty_page_has_no_sentences(self):
        author = Author(site="alice")
        assert sentence_count(author.weave) == 0


class TestScores:
    def sample(self) -> Author:
        author = Author(site="alice")
        author.type_at(0, "The cat sat on the mat. The dog ran far.")
        return author

    def test_the_sample_syllable_total_is_measured(self):
        assert syllable_total(self.sample().weave) == 10

    def test_the_reading_ease_is_the_measured_figure(self):
        assert flesch_reading_ease(self.sample().weave) == 117.2

    def test_the_grade_is_the_measured_figure(self):
        assert flesch_kincaid_grade(self.sample().weave) == -1.8

    def test_an_empty_page_scores_zero_not_a_lie(self):
        author = Author(site="alice")
        assert flesch_reading_ease(author.weave) == 0.0
        assert flesch_kincaid_grade(author.weave) == 0.0


class TestReport:
    def test_the_report_disavows_grading_thought(self):
        author = Author(site="alice")
        author.type_at(0, "Some prose to measure here.")
        assert "not thought" in report(author.weave)

    def test_an_empty_page_reports_nothing_to_measure(self):
        author = Author(site="alice")
        assert "needs words" in report(author.weave)
