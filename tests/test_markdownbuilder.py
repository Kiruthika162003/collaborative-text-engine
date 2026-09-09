from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.markdownbuilder import MarkdownBuilder


class TestBlocks:
    def test_heading_and_paragraph(self):
        out = MarkdownBuilder().heading(1, "Title").paragraph("intro").render()
        assert out == "# Title\n\nintro"

    def test_bullets_render_as_a_list(self):
        out = MarkdownBuilder().bullets(["a", "b"]).render()
        assert out == "- a\n- b"

    def test_numbered_lists_count(self):
        out = MarkdownBuilder().numbered(["x", "y"]).render()
        assert out == "1. x\n2. y"

    def test_a_code_block_is_fenced(self):
        out = MarkdownBuilder().code("print(1)", "python").render()
        assert out == "```python\nprint(1)\n```"

    def test_a_quote_is_prefixed(self):
        out = MarkdownBuilder().quote("noted").render()
        assert out == "> noted"


class TestSpacing:
    def test_blocks_are_separated_by_a_blank_line(self):
        out = (
            MarkdownBuilder()
            .heading(2, "H")
            .paragraph("p")
            .bullets(["one"])
            .render()
        )
        assert out == "## H\n\np\n\n- one"


class TestGuards:
    def test_a_bad_heading_level_is_refused(self):
        with pytest.raises(Invalid):
            MarkdownBuilder().heading(7, "too deep")

    def test_block_count_tracks_additions(self):
        builder = MarkdownBuilder().heading(1, "a").paragraph("b")
        assert builder.block_count() == 2
