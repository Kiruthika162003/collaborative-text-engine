from __future__ import annotations

from loom.trials.anchortrial import run


class TestAnchortrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_every_pinned_layer_held(self):
        verdict = run()
        assert verdict.numbers["mark_holds"]
        assert verdict.numbers["bookmark_holds"]
        assert verdict.numbers["comment_quote_holds"]

    def test_the_storm_actually_ran(self):
        verdict = run()
        assert verdict.numbers["storm_rounds"] == 40
