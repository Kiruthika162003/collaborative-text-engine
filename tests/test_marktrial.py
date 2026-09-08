from __future__ import annotations

from loom.trials.marktrial import run


class TestMarktrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_the_regret_shelves_then_drains(self):
        verdict = run()
        assert verdict.numbers["early_unmark_shelved"]
        assert verdict.numbers["mark_arrival_drains"]

    def test_both_wardrobes_compare_equal_as_data(self):
        verdict = run()
        assert verdict.numbers["spans_equal"]
        assert verdict.numbers["spans"] == (
            (
                "plain bold plain",
                frozenset({"italic"}),
            ),
        )

    def test_one_standing_one_stripped_in_each_house(
        self,
    ):
        verdict = run()
        assert verdict.numbers["standing_each"] == (
            1,
            1,
        )
        assert verdict.numbers["stripped_each"] == (
            1,
            1,
        )
