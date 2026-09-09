"""State machine: a finite automaton of states, events, and the transitions between.

Many systems are naturally a set of states and the events that
move between them, a turnstile locked and unlocked, a document
draft and review and published, and this models that directly.
A transition says that in a given state a given event leads to a
given next state, and firing an event looks up the transition
for the current state and moves there, so the machine's whole
behaviour is the table of transitions and the current state
walking it. Firing an event with no transition from the current
state is refused rather than ignored, because in a well-modelled
machine every event that can happen in a state has a defined
outcome, and an event with no transition is either a bug in the
model or an input that should have been rejected earlier, and
silently staying put would hide which. A caller who wants an
event to be a harmless no-op in some state adds a transition
back to the same state, which makes the intent explicit rather
than implicit in the absence of a rule. The reachable-states
query walks the transitions from the current state to find every
state the machine could still get to, which answers the question
a designer asks of a machine, whether a state is a dead end or
still connected to the rest, and catches a published state that
can never be left or a state nothing leads to. The building
calls return the machine so a whole automaton defines in one
chained expression, and the states and events are whatever
hashable values a caller uses, strings usually, since a state
machine cares about identity and transition, not about what the
states mean.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid


@dataclass
class StateMachine:
    state: str
    transitions: dict = field(default_factory=dict)

    def add(self, from_state, event, to_state) -> StateMachine:
        self.transitions[(from_state, event)] = to_state
        return self

    def can_fire(self, event) -> bool:
        return (self.state, event) in self.transitions

    def fire(self, event):
        key = (self.state, event)
        if key not in self.transitions:
            raise Invalid(
                f"no transition for event {event!r} from state {self.state!r}"
            )
        self.state = self.transitions[key]
        return self.state

    def reachable(self) -> list:
        seen = {self.state}
        queue = [self.state]
        while queue:
            current = queue.pop(0)
            for (from_state, _event), to_state in self.transitions.items():
                if from_state == current and to_state not in seen:
                    seen.add(to_state)
                    queue.append(to_state)
        return sorted(seen)
