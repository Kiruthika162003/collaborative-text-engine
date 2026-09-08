from __future__ import annotations

from loom.trials.citetrial import run


class TestCitetrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_the_replicas_number_alike(self):
        verdict = run()
        assert verdict.numbers["same_numbering"]
        assert verdict.numbers["same_works_cited"]

    def test_the_merge_kept_four_distinct_sources(self):
        verdict = run()
        assert verdict.numbers["distinct_sources"] == 4

    def test_all_four_citations_landed(self):
        verdict = run()
        assert verdict.numbers["total_marks"] == 4
