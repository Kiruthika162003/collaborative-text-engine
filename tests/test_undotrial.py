from __future__ import annotations

from loom.trials.undotrial import run


class TestUndotrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_the_regret_leaves_and_returns(self):
        verdict = run()
        assert verdict.numbers["after_undo"] == (
            "steady [bob] "
        )
        assert verdict.numbers["after_redo"] == (
            "steady [bob] regret!"
        )

    def test_the_concurrent_hand_survives(self):
        verdict = run()
        assert verdict.numbers["bob_survives"]

    def test_redo_returns_fresh_not_ghostly(self):
        verdict = run()
        assert verdict.numbers["redo_ops"] == 7
        assert verdict.numbers["redo_is_fresh"]
