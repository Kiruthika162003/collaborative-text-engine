from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.statemachine import StateMachine


def turnstile() -> StateMachine:
    machine = StateMachine("locked")
    machine.add("locked", "coin", "unlocked")
    machine.add("unlocked", "push", "locked")
    return machine


class TestFire:
    def test_an_event_moves_state(self):
        machine = turnstile()
        assert machine.fire("coin") == "unlocked"
        assert machine.fire("push") == "locked"

    def test_can_fire_reports_valid_events(self):
        machine = turnstile()
        assert machine.can_fire("coin")
        assert not machine.can_fire("push")

    def test_an_undefined_event_is_refused(self):
        with pytest.raises(Invalid):
            turnstile().fire("push")


class TestReachable:
    def test_all_states_are_reachable(self):
        assert turnstile().reachable() == ["locked", "unlocked"]

    def test_a_dead_end_is_visible(self):
        machine = StateMachine("start")
        machine.add("start", "go", "middle")
        machine.add("middle", "stop", "end")
        assert machine.reachable() == ["end", "middle", "start"]

    def test_an_unreachable_state_is_absent(self):
        machine = StateMachine("a")
        machine.add("a", "x", "b")
        machine.add("island", "y", "island")
        assert "island" not in machine.reachable()
