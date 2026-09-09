from __future__ import annotations

from loom.trials.casetrial import run


class TestCasetrial:
    def test_the_verdict_holds(self):
        assert run().holds

    def test_alice_sheared_all_five_letters(self):
        assert run().numbers["shears_by_alice"] == 5

    def test_the_replicas_converge(self):
        numbers = run().numbers
        assert numbers["one_digest"]
        assert numbers["texts_equal"]

    def test_the_concurrent_glyph_survived(self):
        assert run().numbers["mark_survived"]
