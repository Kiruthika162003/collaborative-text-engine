"""The scheduler: deciding when a sync is worth its bandwidth, and saying why.

Syncing on every keystroke floods the wire and syncing
never strands the replicas, so the scheduler picks the
middle by weighing what a sync would carry against what it
would cost. It tracks the count of local operations minted
since the last sync, the ticks elapsed, and decides to sync
when either the backlog crosses a threshold, enough has
changed to be worth a round trip, or the idle time crosses
one, a pause being the cheapest moment to spend bandwidth
because nobody is waiting on the keystroke that did not
come. Every decision carries its reason, backlog or idle or
hold, because a scheduler that syncs without saying why
cannot be tuned, and one that cannot be tuned gets replaced
by a fixed interval that is wrong twice a day. The
thresholds are parameters with defaults, the clock is
logical and injected, and recording a sync resets both
counters, so the next decision measures from the reunion
rather than from the dawn of the session.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Invalid

BACKLOG_THRESHOLD = 20
IDLE_THRESHOLD = 5


@dataclass
class SyncScheduler:
    backlog_threshold: int = BACKLOG_THRESHOLD
    idle_threshold: int = IDLE_THRESHOLD
    backlog: int = 0
    last_change_tick: int = 0
    last_sync_tick: int = 0
    syncs: int = 0

    def __post_init__(self) -> None:
        if (
            self.backlog_threshold < 1
            or self.idle_threshold < 1
        ):
            raise Invalid(
                "thresholds below one sync on every "
                "keystroke, which is the flood the "
                "scheduler exists to prevent"
            )

    def minted(self, count: int, tick: int) -> None:
        self.backlog += count
        self.last_change_tick = tick

    def decide(self, now: int) -> str:
        if self.backlog == 0:
            return "hold: nothing to sync"
        if self.backlog >= self.backlog_threshold:
            return (
                f"sync: backlog of {self.backlog} "
                "crossed the threshold, worth a round "
                "trip"
            )
        if (
            now - self.last_change_tick
            >= self.idle_threshold
        ):
            return (
                f"sync: idle {now - self.last_change_tick} "
                "tick(s), the cheapest moment to spend "
                "bandwidth"
            )
        return (
            f"hold: {self.backlog} waiting, still "
            "typing"
        )

    def should_sync(self, now: int) -> bool:
        return self.decide(now).startswith("sync")

    def record_sync(self, now: int) -> str:
        carried = self.backlog
        self.backlog = 0
        self.last_sync_tick = now
        self.syncs += 1
        return (
            f"synced {carried} operation(s); the next "
            "decision measures from here"
        )
