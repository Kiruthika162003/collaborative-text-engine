from __future__ import annotations

from loom.trials.relaytrial import run


class TestRelaytrial:
    def test_the_verdict_holds(self):
        assert run().holds

    def test_reversed_delivery_converges(self):
        numbers = run().numbers
        assert numbers["one_digest"]
        assert numbers["converged_text"] == "the brown fox"

    def test_the_shelf_peaked_one_below_the_run_and_drained(self):
        numbers = run().numbers
        assert numbers["peak_shelf"] == numbers["run_length"] - 1
        assert numbers["still_waiting"] == 0

    def test_every_glyph_wove(self):
        numbers = run().numbers
        assert numbers["woven"] == numbers["run_length"]
