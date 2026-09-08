from __future__ import annotations

from examples import (
    collabnight,
    pairday,
    researchday,
    reviewday,
    trainday,
    writingday,
)


class TestCollabNight:
    def test_the_night_reads_end_to_end(self, capsys):
        assert collabnight.main() == 0
        out = capsys.readouterr().out
        assert "session night, 2 ticket(s):" in out
        assert (
            "bob seated as a writer; the ticket is "
            "spent"
        ) in out
        assert (
            "text:    'the rough draft needs work'"
        ) in out
        assert "'rough' wears bold" in out
        assert "bob on 'rough': too harsh?" in out
        assert (
            "the rough draft [+needs work+ bob]"
        ) in out
        assert "words:   5" in out


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


class TestResearchDay:
    def test_the_day_reads_end_to_end(self, capsys):
        assert researchday.main() == 0
        out = capsys.readouterr().out
        assert "Field Notes" in out
        assert "[1] Rees, M (2018). Flood Watch." in out
        assert "sentences: 4" in out
        assert "ease:      94.2" in out
        assert "pages:     2 at one line each" in out
        assert "1 handoff(s) between hands" in out
        assert "authorship: alice 78%, bob 22%" in out
        assert "reads as a monologue" in out


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
