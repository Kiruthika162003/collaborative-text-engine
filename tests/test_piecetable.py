from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.piecetable import PieceTable


class TestReadBack:
    def test_an_empty_table_reads_as_empty(self):
        table = PieceTable()
        assert table.text() == ""
        assert len(table) == 0

    def test_the_original_reads_back_whole(self):
        table = PieceTable("hello world")
        assert table.text() == "hello world"
        assert len(table) == 11


class TestInsert:
    def test_insert_at_the_end_appends(self):
        table = PieceTable("hello")
        table.insert(5, " world")
        assert table.text() == "hello world"

    def test_insert_at_the_start_prepends(self):
        table = PieceTable("world")
        table.insert(0, "hello ")
        assert table.text() == "hello world"

    def test_insert_in_the_middle_splits_a_piece(self):
        table = PieceTable("held")
        table.insert(2, "llo, wor")
        assert table.text() == "hello, world"
        assert table.piece_count() == 3

    def test_insert_into_an_empty_table(self):
        table = PieceTable()
        table.insert(0, "first")
        assert table.text() == "first"

    def test_an_out_of_range_insert_is_refused(self):
        with pytest.raises(Invalid):
            PieceTable("abc").insert(9, "x")


class TestDelete:
    def test_delete_a_middle_range(self):
        table = PieceTable("hello world")
        table.delete(5, 6)
        assert table.text() == "hello"

    def test_delete_from_the_front(self):
        table = PieceTable("hello world")
        table.delete(0, 6)
        assert table.text() == "world"

    def test_delete_spanning_a_split(self):
        table = PieceTable("abcdef")
        table.insert(3, "XYZ")
        assert table.text() == "abcXYZdef"
        table.delete(2, 5)
        assert table.text() == "abef"

    def test_a_zero_length_delete_changes_nothing(self):
        table = PieceTable("abc")
        table.delete(1, 0)
        assert table.text() == "abc"

    def test_an_out_of_bounds_delete_is_refused(self):
        with pytest.raises(Invalid):
            PieceTable("abc").delete(2, 5)


class TestReplaceAndSubstring:
    def test_replace_swaps_a_range(self):
        table = PieceTable("the quick fox")
        table.replace(4, 5, "slow")
        assert table.text() == "the slow fox"

    def test_substring_reads_a_slice(self):
        table = PieceTable("hello world")
        table.insert(5, ",")
        assert table.substring(0, 6) == "hello,"


class TestAgainstNaiveString:
    def test_a_run_of_edits_matches_plain_string_ops(self):
        table = PieceTable("the sun rose over the hill")
        shadow = "the sun rose over the hill"

        edits = [
            ("insert", 3, " bright"),
            ("delete", 0, 4),
            ("insert", 0, "When "),
            ("delete", 10, 5),
            ("insert", 10, " climbed"),
        ]
        for kind, offset, payload in edits:
            if kind == "insert":
                table.insert(offset, payload)
                shadow = shadow[:offset] + payload + shadow[offset:]
            else:
                length = int(payload)
                table.delete(offset, length)
                shadow = shadow[:offset] + shadow[offset + length :]
            assert table.text() == shadow
