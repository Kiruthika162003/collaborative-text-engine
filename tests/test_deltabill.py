from __future__ import annotations

from loom.trials.deltabill import run


class TestDeltabill:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_the_reunion_has_its_shape(self):
        verdict = run()
        assert verdict.numbers["shipped"] == 8
        assert verdict.numbers["converged"]

    def test_the_naive_price_is_taken_before_the_shake(
        self,
    ):
        verdict = run()
        assert (
            verdict.numbers["naive_cost_both_ways"]
            == 208
        )
        assert verdict.numbers["savings_ratio"] == 26

    def test_both_journals_reunite_at_full_memory(self):
        verdict = run()
        assert verdict.numbers["alice_journal"] == 108
        assert verdict.numbers["bob_journal"] == 108
