from __future__ import annotations

from loom.numberdetect import find_numbers, of_kind, total


class TestClassify:
    def test_kinds_are_read_from_the_surface(self):
        found = {n.text: n.kind for n in find_numbers(
            "$5.00 is 50% of 1,000 or 3.14 or 7"
        )}
        assert found["$5.00"] == "currency"
        assert found["50%"] == "percent"
        assert found["1,000"] == "grouped"
        assert found["3.14"] == "decimal"
        assert found["7"] == "integer"

    def test_values_strip_the_marks(self):
        by_text = {n.text: n.value for n in find_numbers("$5.00 50% 1,000")}
        assert by_text["$5.00"] == 5.0
        assert by_text["50%"] == 50.0
        assert by_text["1,000"] == 1000.0


class TestQueries:
    def test_of_kind_filters(self):
        currencies = of_kind("$5 and $10 and 3", "currency")
        assert [c.value for c in currencies] == [5.0, 10.0]

    def test_total_sums_the_values(self):
        assert total("1 2 3") == 6.0

    def test_prose_without_numbers_finds_none(self):
        assert find_numbers("no numbers here") == []
