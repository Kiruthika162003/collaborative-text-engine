from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.gapbuffer import GapBuffer


class TestReadBack:
    def test_an_empty_buffer_reads_empty(self):
        buffer = GapBuffer()
        assert buffer.text() == ""
        assert len(buffer) == 0

    def test_the_seed_text_reads_back(self):
        buffer = GapBuffer("hello")
        assert buffer.text() == "hello"
        assert len(buffer) == 5
        assert buffer.cursor == 5


class TestInsert:
    def test_typing_at_the_end(self):
        buffer = GapBuffer("hello")
        buffer.insert(" world")
        assert buffer.text() == "hello world"

    def test_typing_after_seeking_into_the_middle(self):
        buffer = GapBuffer("held")
        buffer.seek(2)
        buffer.insert("llo, wor")
        assert buffer.text() == "hello, world"

    def test_typing_more_than_the_gap_holds_grows_it(self):
        buffer = GapBuffer("ab", gap=2)
        buffer.insert("cdefghijkl")
        assert buffer.text() == "abcdefghijkl"

    def test_the_cursor_tracks_typed_length(self):
        buffer = GapBuffer("")
        buffer.insert("abc")
        assert buffer.cursor == 3


class TestDeletion:
    def test_backspace_removes_before_the_cursor(self):
        buffer = GapBuffer("hello")
        buffer.backspace(2)
        assert buffer.text() == "hel"

    def test_delete_removes_after_the_cursor(self):
        buffer = GapBuffer("hello")
        buffer.seek(0)
        buffer.delete(2)
        assert buffer.text() == "llo"

    def test_backspace_is_clamped_to_the_start(self):
        buffer = GapBuffer("ab")
        assert buffer.backspace(9) == 2
        assert buffer.text() == ""

    def test_delete_is_clamped_to_the_end(self):
        buffer = GapBuffer("ab")
        buffer.seek(0)
        assert buffer.delete(9) == 2
        assert buffer.text() == ""


class TestGuards:
    def test_seek_out_of_range_is_refused(self):
        with pytest.raises(Invalid):
            GapBuffer("abc").seek(9)

    def test_a_negative_backspace_is_refused(self):
        with pytest.raises(Invalid):
            GapBuffer("abc").backspace(-1)


class TestAgainstNaiveString:
    def test_clustered_edits_match_plain_string_ops(self):
        buffer = GapBuffer("the sun rose over the hill")
        shadow = "the sun rose over the hill"

        steps = [
            ("seek", 3),
            ("insert", " bright"),
            ("seek", 0),
            ("insert", "When "),
            ("seek", 5),
            ("delete", 4),
        ]
        cursor = len(shadow)
        for kind, value in steps:
            if kind == "seek":
                cursor = value
                buffer.seek(value)
            elif kind == "insert":
                shadow = shadow[:cursor] + value + shadow[cursor:]
                cursor += len(value)
                buffer.insert(value)
            else:
                shadow = shadow[:cursor] + shadow[cursor + value :]
                buffer.delete(value)
            assert buffer.text() == shadow
            assert buffer.cursor == cursor
