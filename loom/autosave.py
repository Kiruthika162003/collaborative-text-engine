"""Autosave: a clean/dirty line and a save that fires only when it must.

A document is dirty when it has changed since the last save
and clean otherwise, and autosave is the discipline that
turns that one bit into the fewest saves that lose no work.
It watches the author's fabric digest: it watches the cloth digest, the visible text
rather than the full fabric, so a change typed and then
undone back to the saved text is correctly clean again, the
bytes being what was saved and the tombstone journey between
not needing a fresh save even though the fabric grew.
Saves fire on two triggers, a quiet interval since the last
change and a hard cap since the last save, the interval
catching the pause after a burst and the cap guaranteeing
that continuous typing still saves eventually, because a
document edited for an hour without a single pause must not
go an hour unsaved. The clock is logical and injected, the
same testability rule every timed thing in the loom obeys,
and every save records the digest it saved so the next
dirty check compares against truth rather than a guess.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.snapshot import cloth_digest
from loom.weave import Weave

QUIET_INTERVAL = 5
HARD_CAP = 30


@dataclass
class Autosave:
    weave: Weave
    quiet_interval: int = QUIET_INTERVAL
    hard_cap: int = HARD_CAP
    saved_digest: str = ""
    last_change_tick: int = 0
    last_save_tick: int = 0
    saves: int = 0

    def __post_init__(self) -> None:
        self.saved_digest = cloth_digest(self.weave)

    def is_dirty(self) -> bool:
        return (
            cloth_digest(self.weave)
            != self.saved_digest
        )

    def touched(self, tick: int) -> None:
        self.last_change_tick = tick

    def should_save(self, now: int) -> bool:
        if not self.is_dirty():
            return False
        quiet = (
            now - self.last_change_tick
            >= self.quiet_interval
        )
        capped = (
            now - self.last_save_tick >= self.hard_cap
        )
        return quiet or capped

    def save(self, now: int) -> str:
        if not self.is_dirty():
            return "clean; nothing to save"
        self.saved_digest = cloth_digest(self.weave)
        self.last_save_tick = now
        self.saves += 1
        return (
            f"saved at tick {now}; the digest saved "
            "is the truth the next dirty check reads"
        )

    def tick(self, now: int) -> str:
        if self.should_save(now):
            reason = (
                "quiet interval"
                if now - self.last_change_tick
                >= self.quiet_interval
                else "hard cap"
            )
            return f"{self.save(now)} ({reason})"
        return "no save needed"
