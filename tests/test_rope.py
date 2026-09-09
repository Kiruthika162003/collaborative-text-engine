from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.rope import Rope


class TestReadBack:
    def test_an_empty_rope_reads_empty(self):
        rope = Rope()
        assert rope.text() == ""
        assert len(rope) == 0

    def test_a_short_text_reads_back(self):
        rope = Rope("hello")
        assert rope.text() == "hello"
        assert len(rope) == 5

    def test_a_text_longer_than_one_leaf_reads_back(self):
        source = "the quick brown fox jumps over the lazy dog"
        rope = Rope(source)
        assert rope.text() == source
        assert len(rope) == len(source)


class TestCharAt:
    def test_char_at_reads_each_position(self):
        source = "abcdefghijklmnopqrstuvwxyz0123456789"
        rope = Rope(source)
        for index, char in enumerate(source):
            assert rope.char_at(index) == char

    def test_an_out_of_range_index_is_refused(self):
        with pytest.raises(Invalid):
            Rope("abc").char_at(3)


class TestConcatAndSplit:
    def test_concat_joins_two_ropes(self):
        joined = Rope("hello ").concat(Rope("world"))
        assert joined.text() == "hello world"

    def test_split_returns_the_two_sides(self):
        left, right = Rope("hello world").split(5)
        assert left.text() == "hello"
        assert right.text() == " world"

    def test_split_at_the_ends_gives_one_empty_side(self):
        left, right = Rope("abc").split(0)
        assert left.text() == ""
        assert right.text() == "abc"

    def test_split_leaves_the_original_readable(self):
        rope = Rope("persistent")
        rope.split(4)
        assert rope.text() == "persistent"


class TestInsertAndDelete:
    def test_insert_into_the_middle(self):
        rope = Rope("held")
        rope.insert(2, "llo, wor")
        assert rope.text() == "hello, world"

    def test_delete_a_range(self):
        rope = Rope("hello world")
        rope.delete(5, 6)
        assert rope.text() == "hello"

    def test_an_out_of_bounds_delete_is_refused(self):
        with pytest.raises(Invalid):
            Rope("abc").delete(2, 5)


class TestRebalance:
    def test_rebalance_preserves_text_and_shortens_depth(self):
        rope = Rope("a")
        for _ in range(60):
            rope = rope.concat(Rope("a"))
        before = rope.depth()
        text_before = rope.text()
        rope.rebalance()
        assert rope.text() == text_before
        assert rope.depth() < before


class TestAgainstNaiveString:
    def test_a_run_of_edits_matches_plain_string_ops(self):
        rope = Rope("the sun rose over the hill and warmed the valley")
        shadow = "the sun rose over the hill and warmed the valley"

        edits = [
            ("insert", 3, " bright"),
            ("delete", 0, 4),
            ("insert", 0, "When "),
            ("delete", 20, 8),
            ("insert", 20, " slowly"),
        ]
        for kind, offset, payload in edits:
            if kind == "insert":
                rope.insert(offset, payload)
                shadow = shadow[:offset] + payload + shadow[offset:]
            else:
                length = int(payload)
                rope.delete(offset, length)
                shadow = shadow[:offset] + shadow[offset + length :]
            assert rope.text() == shadow
            assert len(rope) == len(shadow)
