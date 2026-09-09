from __future__ import annotations

from loom.codespans import contents, spans, unclosed


class TestSpans:
    def test_a_simple_span_is_found(self):
        assert contents("use `code` here") == ["code"]

    def test_a_double_backtick_span_holds_a_backtick(self):
        assert contents("``a`b`` end") == ["a`b"]

    def test_two_spans_are_found(self):
        assert contents("`one` and `two`") == ["one", "two"]

    def test_the_span_positions_are_reported(self):
        span = spans("x `y` z")[0]
        assert span.start == 2
        assert span.end == 5


class TestUnclosed:
    def test_an_unclosed_backtick_is_flagged(self):
        assert unclosed("`open")

    def test_a_closed_span_is_not_unclosed(self):
        assert not unclosed("`ok`")

    def test_prose_without_backticks_is_closed(self):
        assert not unclosed("plain text")
