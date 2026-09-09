from __future__ import annotations

from loom.barchart import bar_length, chart


class TestChart:
    def test_the_largest_value_fills_the_width(self):
        rendered = chart([("a", 10), ("b", 5)], width=40)
        rows = rendered.splitlines()
        assert rows[0].count("#") == 40
        assert rows[1].count("#") == 20

    def test_the_value_is_printed_after_the_bar(self):
        rendered = chart([("a", 7)], width=10)
        assert rendered.endswith(" 7")

    def test_labels_are_right_aligned(self):
        rendered = chart([("aa", 1), ("b", 1)])
        rows = rendered.splitlines()
        assert rows[0].startswith("aa |")
        assert rows[1].startswith(" b |")

    def test_zero_shows_no_bar(self):
        rendered = chart([("z", 0), ("a", 10)])
        assert rendered.splitlines()[0].count("#") == 0

    def test_empty_data_says_so(self):
        assert chart([]) == "no data to chart"


class TestBarLength:
    def test_length_scales_to_the_biggest(self):
        assert bar_length(5, 10, width=40) == 20

    def test_a_zero_biggest_is_safe(self):
        assert bar_length(3, 0) == 0
