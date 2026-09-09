from __future__ import annotations

from loom.trials.patchtrial import run


class TestPatchtrial:
    def test_the_verdict_holds(self):
        assert run().holds

    def test_the_patch_was_surgical(self):
        numbers = run().numbers
        assert numbers["patch_ops"] < numbers["base_length"]

    def test_the_swap_and_the_concurrent_edit_both_survive(self):
        numbers = run().numbers
        assert numbers["swap_present"]
        assert numbers["concurrent_present"]

    def test_the_replicas_converge(self):
        assert run().numbers["one_digest"]
