from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.registers import EveryVoice, LastWriter, Write


class TestLastWriter:
    def test_more_witnessed_holds_the_pen(self):
        register = LastWriter()
        register.write(
            Write(site="alice", rank=5, value="Draft")
        )
        receipt = register.write(
            Write(site="bob", rank=3, value="Old")
        )
        assert "yields" in receipt
        assert register.read() == "Draft"

    def test_causally_later_outranks_everywhere(self):
        one = LastWriter()
        two = LastWriter()
        first = Write(
            site="alice", rank=2, value="Mine"
        )
        second = Write(
            site="bob", rank=7, value="Better"
        )
        one.write(first)
        one.write(second)
        two.write(second)
        two.write(first)
        assert one.read() == two.read() == "Better"

    def test_rank_ties_break_by_site_identically(self):
        one = LastWriter()
        two = LastWriter()
        left = Write(site="alice", rank=4, value="A")
        right = Write(site="bob", rank=4, value="B")
        one.write(left)
        one.write(right)
        two.write(right)
        two.write(left)
        assert one.read() == two.read() == "B"

    def test_the_unwritten_pretends_nothing(self):
        with pytest.raises(Invalid):
            LastWriter().read()


class TestEveryVoice:
    def test_equal_ranks_stand_together(self):
        register = EveryVoice()
        register.write(
            Write(site="alice", rank=4, value="North")
        )
        receipt = register.write(
            Write(site="bob", rank=4, value="South")
        )
        assert "stands beside 1 other(s)" in receipt
        assert register.read() == [
            ("alice", "North"),
            ("bob", "South"),
        ]
        assert not register.settled()
        assert "ties have no winners here" in (
            register.page()
        )

    def test_a_higher_rank_dissolves_the_tie(self):
        register = EveryVoice()
        register.write(
            Write(site="alice", rank=4, value="North")
        )
        register.write(
            Write(site="bob", rank=4, value="South")
        )
        receipt = register.write(
            Write(site="cara", rank=9, value="East")
        )
        assert "dissolves 2 earlier voice(s)" in receipt
        assert register.settled()
        assert register.page() == (
            "settled: 'East' by cara"
        )

    def test_writing_twice_stands_once(self):
        register = EveryVoice()
        entry = Write(site="alice", rank=4, value="X")
        register.write(entry)
        receipt = register.write(entry)
        assert "one voice, one entry" in receipt
        assert len(register.standing) == 1

    def test_order_of_arrival_changes_nothing(self):
        writes = [
            Write(site="alice", rank=4, value="N"),
            Write(site="bob", rank=4, value="S"),
            Write(site="cara", rank=6, value="E"),
        ]
        one = EveryVoice()
        two = EveryVoice()
        for entry in writes:
            one.write(entry)
        for entry in reversed(writes):
            two.write(entry)
        assert one.read() == two.read()

    def test_silence_reads_as_silence(self):
        assert EveryVoice().page() == (
            "no voice has spoken"
        )
