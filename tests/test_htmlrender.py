from __future__ import annotations

from loom.htmlrender import render


class TestBlocks:
    def test_a_heading_renders(self):
        assert render("# Title") == "<h1>Title</h1>"

    def test_a_paragraph_renders(self):
        assert render("just prose") == "<p>just prose</p>"

    def test_an_unordered_list_renders(self):
        assert render("- a\n- b") == "<ul><li>a</li><li>b</li></ul>"

    def test_an_ordered_list_renders(self):
        assert render("1. a\n2. b") == "<ol><li>a</li><li>b</li></ol>"

    def test_a_blockquote_renders(self):
        assert render("> hi") == "<blockquote><p>hi</p></blockquote>"

    def test_a_code_fence_renders_verbatim(self):
        assert render("```\nx = 1\n```") == "<pre><code>x = 1</code></pre>"


class TestInline:
    def test_bold_and_italic_and_code(self):
        out = render("a **b** *c* `d`")
        assert "<strong>b</strong>" in out
        assert "<em>c</em>" in out
        assert "<code>d</code>" in out

    def test_a_link_renders(self):
        assert render("[t](http://x)") == '<p><a href="http://x">t</a></p>'


class TestSafety:
    def test_content_angle_brackets_are_escaped(self):
        assert render("a < b > c") == "<p>a &lt; b &gt; c</p>"

    def test_code_content_is_not_inline_processed(self):
        # a star inside inline code stays a star, not emphasis
        assert render("`a * b`") == "<p><code>a * b</code></p>"

    def test_fenced_code_is_escaped(self):
        assert render("```\n<tag>\n```") == "<pre><code>&lt;tag&gt;</code></pre>"
