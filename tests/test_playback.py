from __future__ import annotations

from loom.author import Author
from loom.playback import Playback
from loom.transcript import Tape


def recorded() -> Tape:
    tape = Tape()
    author = Author(site="alice", tape=tape)
    author.type_at(0, "cat")
    author.erase_at(1, 1)
    author.type_at(1, "u")
    return tape


class TestStepping:
    def test_the_document_unfolds_one_gesture(self):
        play = Playback(tape=recorded())
        assert play.text_now() == ""
        play.step()
        assert play.text_now() == "c"
        play.step()
        play.step()
        assert play.text_now() == "cat"

    def test_a_step_narrates_in_human_terms(self):
        play = Playback(tape=recorded())
        assert "typed 'c'" in play.step()
        play.step()
        play.step()
        assert "struck" in play.step()

    def test_scrubbing_back_needs_no_undo_stack(self):
        play = Playback(tape=recorded())
        play.seek(3)
        assert play.text_now() == "cat"
        play.back()
        assert play.text_now() == "ca"
        play.seek(5)
        assert play.text_now() == "cut"


class TestEdges:
    def test_the_end_clamps_and_says_so(self):
        play = Playback(tape=recorded())
        play.seek(999)
        assert "clamped to the tape's edge" in (
            play.seek(999)
        )
        assert "nothing left to play" in play.step()

    def test_the_start_clamps_and_says_so(self):
        play = Playback(tape=recorded())
        assert "nothing behind to rewind" in play.back()

    def test_progress_reads_as_a_fraction(self):
        play = Playback(tape=recorded())
        play.seek(2)
        assert "step 2 of 5" in play.progress()
        assert "(40%)" in play.progress()
