from __future__ import annotations

from loom.author import Author
from loom.cadence import (
    bursts,
    busiest_hand,
    handoffs,
    report,
)
from loom.transcript import Tape


class TestBursts:
    def test_a_solo_tape_is_one_burst(self):
        tape = Tape()
        author = Author(site="alice", tape=tape)
        author.type_at(0, "monologue")
        runs = bursts(tape)
        assert len(runs) == 1
        assert handoffs(tape) == 0

    def test_turns_become_separate_bursts(self):
        tape = Tape()
        alice = Author(site="alice", tape=tape)
        alice.type_at(0, "ab")
        bob_ops = Author(site="bob").type_at(0, "cd")
        for op in bob_ops:
            tape.record(op)
        alice.type_at(0, "e")
        runs = bursts(tape)
        assert [r.site for r in runs] == [
            "alice",
            "bob",
            "alice",
        ]
        assert handoffs(tape) == 2

    def test_the_busiest_hand_is_by_gestures(self):
        tape = Tape()
        alice = Author(site="alice", tape=tape)
        alice.type_at(0, "aaaaa")
        bob_ops = Author(site="bob").type_at(0, "b")
        for op in bob_ops:
            tape.record(op)
        assert busiest_hand(tape) == "alice"


class TestReport:
    def test_the_report_names_the_rhythm(self):
        tape = Tape()
        alice = Author(site="alice", tape=tape)
        alice.type_at(0, "abc")
        bob_ops = Author(site="bob").type_at(0, "xy")
        for op in bob_ops:
            tape.record(op)
        page = report(tape)
        assert "2 burst(s)" in page
        assert "1 handoff(s)" in page
        assert "cadence measures work" in page

    def test_an_empty_tape_has_no_rhythm(self):
        assert "no rhythm" in report(Tape())
