from __future__ import annotations

from loom.author import Author
from loom.columns import display_width
from loom.pipetables import find_tables, parse, render

SIMPLE = "| Name | Age |\n| :--- | ---: |\n| Al | 3 |\n| Bianca | 40 |"


class TestParse:
    def test_a_table_parses_headers_and_rows(self):
        table = parse(SIMPLE)
        assert table.headers == ["Name", "Age"]
        assert table.rows == [["Al", "3"], ["Bianca", "40"]]

    def test_alignments_come_from_the_colons(self):
        table = parse(SIMPLE)
        assert table.alignments == ["left", "right"]

    def test_pipes_without_a_separator_are_not_a_table(self):
        assert parse("| a | b |\n| c | d |") is None

    def test_a_center_alignment_is_read(self):
        table = parse("| h |\n| :-: |\n| x |")
        assert table.alignments == ["center"]


class TestRender:
    def test_columns_are_padded_to_width(self):
        rendered = render(parse(SIMPLE))
        lines = rendered.split("\n")
        assert lines[0] == "| Name   | Age |"
        assert lines[3] == "| Bianca |  40 |"

    def test_render_is_idempotent(self):
        once = render(parse(SIMPLE))
        twice = render(parse(once))
        assert once == twice

    def test_a_ragged_row_is_padded_not_dropped(self):
        table = parse("| A | B |\n| - | - |\n| solo |")
        rendered = render(table)
        assert rendered.split("\n")[2].startswith("| solo |")
        assert len(table.rows) == 1

    def test_an_extra_cell_is_kept(self):
        table = parse("| A | B |\n| - | - |\n| a | b | c |")
        assert "c" in render(table).split("\n")[2]


class TestWideGlyphs:
    def test_a_wide_column_aligns_by_display_width(self):
        table = parse("| 名 | x |\n| - | - |\n| 中文 | y |")
        rendered = render(table)
        first_col = [
            line.split("|")[1] for line in rendered.split("\n")
        ]
        widths = {display_width(cell) for cell in first_col}
        assert len(widths) == 1


class TestFind:
    def test_a_table_embedded_in_prose_is_found(self):
        author = Author(site="alice")
        author.type_at(
            0,
            "intro\n\n| A | B |\n| - | - |\n| 1 | 2 |\n\nafter",
        )
        tables = find_tables(author.weave)
        assert len(tables) == 1
        assert tables[0].headers == ["A", "B"]

    def test_prose_without_a_table_finds_none(self):
        author = Author(site="alice")
        author.type_at(0, "just words | with a pipe")
        assert find_tables(author.weave) == []
