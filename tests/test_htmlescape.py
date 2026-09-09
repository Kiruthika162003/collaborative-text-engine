from __future__ import annotations

from loom.htmlescape import escape, needs_escape, unescape


class TestEscape:
    def test_angle_brackets_are_escaped(self):
        assert escape("a<b>c") == "a&lt;b&gt;c"

    def test_the_ampersand_is_escaped_first(self):
        assert escape("a&b") == "a&amp;b"
        assert escape("<&>") == "&lt;&amp;&gt;"

    def test_quotes_are_escaped(self):
        assert escape('"x" \'y\'') == "&quot;x&quot; &#39;y&#39;"

    def test_plain_text_is_untouched(self):
        assert escape("plain text 123") == "plain text 123"


class TestUnescape:
    def test_entities_decode(self):
        assert unescape("a&lt;b&amp;c") == "a<b&c"


class TestRoundTrip:
    def test_escape_then_unescape_is_identity(self):
        for sample in ["a<b>", "x&y", '"q"', "safe", "<&>\"'"]:
            assert unescape(escape(sample)) == sample


class TestNeeds:
    def test_needs_escape_detects_a_special(self):
        assert needs_escape("a<b")
        assert not needs_escape("abc")
