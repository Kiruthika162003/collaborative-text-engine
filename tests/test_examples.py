from __future__ import annotations

from examples import pairday


class TestPairDay:
    def test_the_day_reads_end_to_end(self, capsys):
        assert pairday.main() == 0
        out = capsys.readouterr().out
        assert (
            "text:    'The plan: test first, "
            "ship tuesday'"
        ) in out
        assert "one digest at both stations" in out
        assert (
            "bob holds the pen; 'The Plan' stands"
        ) in out
        assert (
            "alice says 'final'; bob says "
            "'needs-work'"
        ) in out
        assert "survives on purpose" in out
        assert "tags: urgent" in out
        assert "shares:  alice 65%, bob 35%" in out
