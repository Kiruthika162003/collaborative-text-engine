from __future__ import annotations

from loom.trials.interleavetrial import run


class TestInterleavetrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_not_a_single_letter_left_its_sentence(
        self,
    ):
        verdict = run()
        assert verdict.numbers["voice_runs"] == 4
        assert verdict.numbers["fragmentation"] == 1.0
        assert verdict.numbers["every_sentence_intact"]

    def test_the_arbitrary_is_identical_everywhere(
        self,
    ):
        verdict = run()
        assert verdict.numbers["order"] == (
            "dana",
            "cara",
            "bob",
            "alice",
        )
