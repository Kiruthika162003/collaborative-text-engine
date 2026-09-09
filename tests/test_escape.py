from __future__ import annotations

from loom.escape import escape, needs_escape, unescape


class TestEscape:
    def test_emphasis_characters_are_protected(self):
        assert escape("*bold*") == "\\*bold\\*"

    def test_brackets_are_protected(self):
        assert escape("[x]") == "\\[x\\]"

    def test_plain_text_is_untouched(self):
        assert escape("plain words 1.2") == "plain words 1.2"


class TestUnescape:
    def test_unescape_strips_the_backslash(self):
        assert unescape("\\*bold\\*") == "*bold*"

    def test_a_backslash_before_a_plain_char_is_kept(self):
        assert unescape("a\\b") == "a\\b"


class TestRoundTrip:
    def test_escape_then_unescape_is_identity(self):
        for sample in ["*a_b*", "[link](url)", "~~x~~", "plain", "a|b<c>"]:
            assert unescape(escape(sample)) == sample


class TestNeeds:
    def test_needs_escape_detects_a_special(self):
        assert needs_escape("a*b")
        assert not needs_escape("abc")
