from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Missing
from loom.ids import OpId
from loom.paragraphs import (
    block_count,
    block_of,
    blocks,
    outline,
)


def three_blocks() -> Author:
    author = Author(site="alice")
    author.type_at(
        0, "first para\n\nsecond para\n\nthird para"
    )
    return author


class TestBlocks:
    def test_blank_lines_split_the_cloth(self):
        author = three_blocks()
        held = blocks(author.weave)
        assert block_count(author.weave) == 3
        assert held[1].text == "second para"

    def test_a_single_newline_stays_in_the_block(self):
        author = Author(site="alice")
        author.type_at(0, "line one\nline two")
        held = blocks(author.weave)
        assert len(held) == 1
        assert held[0].text == "line one line two"

    def test_the_void_between_is_not_a_paragraph(self):
        author = Author(site="alice")
        author.type_at(0, "a\n\n\n\nb")
        assert block_count(author.weave) == 2


class TestPins:
    def test_a_pin_survives_paragraphs_added_above(self):
        author = three_blocks()
        third_pin = blocks(author.weave)[2].pin
        author.type_at(0, "zero para\n\n")
        held = blocks(author.weave)
        moved = next(
            block
            for block in held
            if block.pin == third_pin
        )
        assert moved.text == "third para"
        assert moved.ordinal == 3

    def test_a_strand_knows_its_block(self):
        author = three_blocks()
        strand = author.weave.strand_at_visible(14)
        assert block_of(author.weave, strand.id) == 1

    def test_an_absent_strand_is_missing(self):
        author = three_blocks()
        with pytest.raises(Missing):
            block_of(
                author.weave,
                OpId(site="ghost", counter=1),
            )


class TestOutline:
    def test_the_outline_names_by_first_words(self):
        author = three_blocks()
        page = outline(author.weave)
        assert "3 paragraph(s):" in page
        assert "0: 'first para'" in page
        assert "2: 'third para'" in page

    def test_a_blank_cloth_has_no_paragraphs(self):
        author = Author(site="alice")
        assert "the cloth is blank" in outline(
            author.weave
        )
