from __future__ import annotations

from loom.trials.mergetrial import run


class TestMergetrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_all_three_paths_agree(self):
        verdict = run()
        assert verdict.numbers["reconciliation_paths"] == 3
        assert verdict.numbers["one_digest"]

    def test_the_union_pays_for_the_base_once(self):
        verdict = run()
        assert verdict.numbers["union_size"] == 125
        assert verdict.numbers["alice_ops"] == 74
        assert verdict.numbers["bob_ops"] == 67
