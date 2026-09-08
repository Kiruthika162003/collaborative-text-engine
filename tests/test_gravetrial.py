from __future__ import annotations

from loom.trials.gravetrial import run


class TestGravetrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_the_sweep_declined_mid_speech(self):
        verdict = run()
        assert verdict.numbers["refused_mid_speech"]

    def test_the_measured_bill_not_the_guessed_one(self):
        verdict = run()
        assert verdict.numbers["graves_before"] == 22
        assert verdict.numbers["strands_at_sweep"] == 117
        assert verdict.numbers["strands_after"] == 95
        assert (
            verdict.numbers["reclaimed_percent"] == 18
        )

    def test_the_loom_stayed_weavable(self):
        verdict = run()
        assert verdict.numbers["one_digest_after"]
        assert verdict.numbers[
            "converged_after_second_storm"
        ]
