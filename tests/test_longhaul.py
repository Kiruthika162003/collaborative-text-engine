from __future__ import annotations

from loom.trials.longhaul import run


class TestLonghaul:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_the_equation_holds_at_size(self):
        verdict = run()
        assert verdict.numbers["typed"] == 580
        assert verdict.numbers["victims"] == 147
        assert verdict.numbers["final_length"] == 433
        assert verdict.numbers["arithmetic_holds"]

    def test_the_mischief_was_plentiful_and_harmless(
        self,
    ):
        verdict = run()
        assert (
            verdict.numbers["duplicates_manufactured"]
            == 1010
        )
        assert verdict.numbers["one_digest"]

    def test_eleven_meetings_of_scissors(self):
        verdict = run()
        assert verdict.numbers["double_cuts"] == 11
