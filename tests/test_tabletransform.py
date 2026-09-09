from __future__ import annotations

from loom.tabletransform import csv_to_pipes, pipes_to_csv


class TestCsvToPipes:
    def test_the_first_row_becomes_the_header(self):
        table = csv_to_pipes("name,age\nAl,3")
        lines = table.split("\n")
        assert lines[0] == "| name | age |"
        assert set(lines[1].replace("|", "").replace(" ", "")) == {"-"}

    def test_empty_csv_makes_no_table(self):
        assert csv_to_pipes("") == ""


class TestPipesToCsv:
    def test_a_table_becomes_csv(self):
        markdown = "| a | b |\n| - | - |\n| 1 | 2 |"
        assert pipes_to_csv(markdown) == "a,b\n1,2"

    def test_non_table_text_makes_no_csv(self):
        assert pipes_to_csv("just prose") == ""

    def test_a_comma_in_a_cell_gets_quoted_in_csv(self):
        markdown = "| a | b |\n| - | - |\n| x,y | z |"
        assert pipes_to_csv(markdown) == 'a,b\n"x,y",z'


class TestRoundTrip:
    def test_csv_survives_a_trip_through_a_table(self):
        csv = "name,age\nAl,3\nBianca,40"
        assert pipes_to_csv(csv_to_pipes(csv)) == csv
