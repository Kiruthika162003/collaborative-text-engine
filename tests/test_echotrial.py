from __future__ import annotations

from loom.trials.echotrial import run


class TestEchotrial:
    def test_the_verdict_holds(self):
        assert run().holds

    def test_duplicate_delivery_converges_like_single_delivery(self):
        numbers = run().numbers
        assert numbers["bob_matches_single_delivery"]
        assert numbers["one_digest"]

    def test_bob_really_heard_the_stream_twice(self):
        numbers = run().numbers
        assert numbers["deliveries_to_bob"] == 2 * numbers["unique_ops"]

    def test_the_word_was_erased_not_doubled(self):
        assert run().numbers["converged_text"] == "the brown fox"
