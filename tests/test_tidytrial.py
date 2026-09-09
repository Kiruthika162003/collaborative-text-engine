from __future__ import annotations

from loom.trials.tidytrial import run


class TestTidytrial:
    def test_the_verdict_holds(self):
        assert run().holds

    def test_tidy_did_real_work(self):
        assert run().numbers["tidy_ops"] > 0

    def test_the_replicas_converge(self):
        assert run().numbers["one_digest"]

    def test_the_concurrent_keystroke_survived(self):
        assert run().numbers["mark_survived"]

    def test_the_bullets_were_normalized(self):
        assert run().numbers["bullets_normalized"]
