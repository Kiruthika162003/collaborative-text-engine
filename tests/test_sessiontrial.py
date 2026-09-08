from __future__ import annotations

from loom.trials.sessiontrial import run


class TestSessiontrial:
    def test_the_verdict_holds(self):
        verdict = run()
        assert verdict.holds

    def test_the_door_admits_and_refuses(self):
        verdict = run()
        assert verdict.numbers["crasher_refused"]
        assert verdict.numbers["tickets_spent"] == 2

    def test_the_fabric_converges_at_matching_digests(
        self,
    ):
        verdict = run()
        assert verdict.numbers["converged"]
        assert verdict.numbers[
            "one_digest_at_convergence"
        ]

    def test_demotion_stops_futures_not_pasts(self):
        verdict = run()
        assert verdict.numbers[
            "bob_words_survive_demotion"
        ]
        assert verdict.numbers["bounce_after_demotion"]
        assert verdict.numbers[
            "bounced_write_stayed_local"
        ]
