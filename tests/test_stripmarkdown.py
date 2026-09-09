from __future__ import annotations

from loom.stripmarkdown import plain, plain_words


class TestBlock:
    def test_heading_hashes_are_removed(self):
        assert plain("# Title") == "Title"

    def test_blockquote_markers_are_removed(self):
        assert plain("> a quote") == "a quote"

    def test_list_markers_are_removed(self):
        assert plain("- item") == "item"
        assert plain("1. item") == "item"


class TestInline:
    def test_bold_and_italic_are_unwrapped(self):
        assert plain("**bold** and *italic*") == "bold and italic"

    def test_underscore_emphasis_is_unwrapped(self):
        assert plain("__b__ and _i_") == "b and i"

    def test_inline_code_is_unwrapped(self):
        assert plain("run `code` now") == "run code now"

    def test_a_link_reduces_to_its_label(self):
        assert plain("see [the docs](http://x)") == "see the docs"

    def test_an_image_reduces_to_its_alt(self):
        assert plain("![a cat](cat.png)") == "a cat"


class TestFences:
    def test_a_fenced_block_keeps_its_code(self):
        assert plain("```\nx = 1\n```") == "x = 1"

    def test_stars_inside_a_fence_are_kept(self):
        assert plain("```\na * b\n```") == "a * b"


class TestWordCount:
    def test_the_word_count_ignores_formatting(self):
        assert plain_words("# Title\n**two** words") == 3
