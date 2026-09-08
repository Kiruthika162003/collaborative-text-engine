from __future__ import annotations

import pytest

from loom.author import Author
from loom.errors import Invalid, Missing
from loom.weave import Insert, Shear


class TestTyping:
    def test_keystrokes_show_immediately(self):
        alice = Author(site="alice")
        alice.type_at(0, "hello")
        assert alice.text() == "hello"
        assert alice.clock.top("alice") == 5

    def test_a_run_chains_its_origins(self):
        alice = Author(site="alice")
        ops = alice.type_at(0, "abc")
        assert ops[0].origin is None
        assert ops[1].origin == ops[0].id
        assert ops[2].origin == ops[1].id

    def test_typing_in_the_middle_anchors_left(self):
        alice = Author(site="alice")
        first = alice.type_at(0, "ad")
        middle = alice.type_at(1, "bc")
        assert alice.text() == "abcd"
        assert isinstance(middle[0], Insert)
        assert middle[0].origin == first[0].id

    def test_typing_nothing_mints_nothing(self):
        with pytest.raises(Invalid):
            Author(site="alice").type_at(0, "")

    def test_typing_past_the_cloth_is_refused(self):
        alice = Author(site="alice")
        alice.type_at(0, "ab")
        with pytest.raises(Missing):
            alice.type_at(9, "x")


class TestErasing:
    def test_erasure_resolves_positions_to_ids(self):
        alice = Author(site="alice")
        typed = alice.type_at(0, "abcd")
        shears = alice.erase_at(1, 2)
        assert alice.text() == "ad"
        assert isinstance(shears[0], Shear)
        assert shears[0].target == typed[1].id
        assert shears[1].target == typed[2].id

    def test_erasing_zero_is_a_gesture_at_nothing(self):
        alice = Author(site="alice")
        alice.type_at(0, "ab")
        with pytest.raises(Invalid):
            alice.erase_at(0, 0)

    def test_the_clock_counts_shears_too(self):
        alice = Author(site="alice")
        alice.type_at(0, "abc")
        alice.erase_at(0, 1)
        assert alice.clock.top("alice") == 4
