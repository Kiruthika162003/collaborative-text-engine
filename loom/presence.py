"""Presence: who is here now, decided by heartbeats against a logical clock.

The little row of avatars that says who is in the document
is presence, and it is the one piece of collaborative state
that is supposed to be forgotten: a hand that stops
beating is gone, and the roster must let it go or the
document looks perpetually crowded with ghosts. Heartbeats
carry a site and the logical tick they were sent at, the
tick injected by the caller rather than read from a wall
clock, because presence tested against real time is
presence that cannot be tested. A hand is present if its
last heartbeat is within the timeout of the current tick,
and away otherwise, computed fresh at every query rather
than stored, so the roster is never stale between updates.
The timeout is a parameter with a stated default, and a
heartbeat from the future is refused rather than trusted,
because a client whose clock leaped ahead would otherwise
appear immortal, present long after it left, which is the
exact ghost the roster exists to banish.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid
from loom.ids import check_site

DEFAULT_TIMEOUT = 30


@dataclass
class Presence:
    timeout: int = DEFAULT_TIMEOUT
    last_beat: dict[str, int] = field(
        default_factory=dict
    )
    now: int = 0

    def beat(self, site: str, tick: int) -> str:
        check_site(site)
        if tick < self.now:
            raise Invalid(
                f"{site} beat at {tick} but the clock "
                f"stands at {self.now}; a heartbeat "
                "from the past cannot revive a hand"
            )
        self.now = max(self.now, tick)
        self.last_beat[site] = tick
        return f"{site} present at tick {tick}"

    def tick(self, now: int) -> None:
        if now < self.now:
            raise Invalid(
                "the presence clock ran backward"
            )
        self.now = now

    def is_present(self, site: str) -> bool:
        beat = self.last_beat.get(site)
        if beat is None:
            return False
        return self.now - beat <= self.timeout

    def present(self) -> list[str]:
        return sorted(
            site
            for site in self.last_beat
            if self.is_present(site)
        )

    def away(self) -> list[str]:
        return sorted(
            site
            for site in self.last_beat
            if not self.is_present(site)
        )

    def roster(self) -> str:
        here = self.present()
        gone = self.away()
        lines = [
            f"{len(here)} here, {len(gone)} away "
            f"(as of tick {self.now})"
        ]
        for site in here:
            lines.append(f"  {site}: present")
        for site in gone:
            lines.append(
                f"  {site}: away, last seen tick "
                f"{self.last_beat[site]}"
            )
        return "\n".join(lines)
