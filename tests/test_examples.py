from __future__ import annotations

from examples import (
    pairday,
    reviewday,
    trainday,
    writingday,
)


class TestWritingDay:
    def test_the_day_reads_end_to_end(self, capsys):
        assert writingday.main() == 0
        out = capsys.readouterr().out
        assert "Trip Plan" in out
        assert "  Packing" in out
        assert "1. tent\n2. stove\n3. maps" in out
        assert "paragraphs: 4" in out
        assert "most-used:  'plan' x3" in out
        assert "links:      1 found" in out
        assert "words:      25" in out


class TestReviewDay:
    def test_the_day_reads_end_to_end(self, capsys):
        assert reviewday.main() == 0
        out = capsys.readouterr().out
        assert (
            "text:    'the very strong draft is done'"
        ) in out
        assert (
            "the very [+strong+ editor][-good-] "
            "draft is[- very-] done"
        ) in out
        assert "editor added 6 glyph(s)" in out
        assert (
            "writer's baseline text lost 9 glyph(s)"
        ) in out
        assert (
            "byline:  writer: 'the very '; editor: "
            "'strong'; writer: ' draft is done'"
        ) in out
        assert "words:   6 surviving" in out


class TestTrainDay:
    def test_the_day_reads_end_to_end(self, capsys):
        assert trainday.main() == 0
        out = capsys.readouterr().out
        assert (
            "text:    'DECISIONotes: do not ship it'"
        ) in out
        assert "fabric:  one digest" in out
        assert (
            "[+DECISION+ bob][-meeting n-]otes: "
            "[+do not + alice]ship it"
        ) in out
        assert (
            "alice replay matches: True; bob replay "
            "matches: True"
        ) in out


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
