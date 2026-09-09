from __future__ import annotations

from loom.charstats import counts, distinct, most_common, report, total


class TestCounts:
    def test_kinds_are_tallied(self):
        tally = counts("ab 12!")
        assert tally["letters"] == 2
        assert tally["digits"] == 2
        assert tally["spaces"] == 1
        assert tally["punctuation"] == 1

    def test_the_counts_sum_to_the_total(self):
        text = "Hello, world! 42 ~"
        assert sum(counts(text).values()) == total(text)

    def test_a_symbol_falls_into_other(self):
        assert counts("~")["other"] == 1

    def test_accented_letters_count_as_letters(self):
        assert counts("é")["letters"] == 1


class TestShape:
    def test_distinct_counts_unique_characters(self):
        assert distinct("aabbc") == 3

    def test_the_most_common_character_is_named(self):
        assert most_common("aaab") == "a"

    def test_empty_text_has_no_common_character(self):
        assert most_common("") is None


class TestReport:
    def test_the_report_counts_and_breaks_down(self):
        page = report("ab 1")
        assert "4 character(s)" in page
        assert "2 letters" in page

    def test_empty_text_reports_nothing(self):
        assert "nothing to count" in report("")
