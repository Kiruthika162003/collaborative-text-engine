from __future__ import annotations

import pytest

from loom.errors import Invalid
from loom.scheduler import SyncScheduler


class TestDeciding:
    def test_nothing_to_sync_holds(self):
        sched = SyncScheduler()
        assert sched.decide(100).startswith("hold")
        assert not sched.should_sync(100)

    def test_a_big_backlog_triggers_a_sync(self):
        sched = SyncScheduler(backlog_threshold=20)
        sched.minted(25, tick=1)
        assert sched.should_sync(2)
        assert "backlog of 25" in sched.decide(2)

    def test_idle_triggers_a_sync(self):
        sched = SyncScheduler(idle_threshold=5)
        sched.minted(3, tick=10)
        assert not sched.should_sync(12)
        assert sched.should_sync(16)
        assert "idle" in sched.decide(16)

    def test_small_backlog_while_typing_holds(self):
        sched = SyncScheduler(
            backlog_threshold=20, idle_threshold=5
        )
        sched.minted(3, tick=10)
        assert sched.decide(11).startswith("hold")


class TestGuards:
    def test_thresholds_below_one_are_refused(self):
        with pytest.raises(Invalid):
            SyncScheduler(backlog_threshold=0)


class TestRecording:
    def test_recording_resets_the_counters(self):
        sched = SyncScheduler(backlog_threshold=5)
        sched.minted(10, tick=1)
        receipt = sched.record_sync(2)
        assert "synced 10 operation(s)" in receipt
        assert sched.backlog == 0
        assert sched.decide(3).startswith("hold")
        assert sched.syncs == 1
