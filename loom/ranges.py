"""Range locks: a stretch of cloth reserved for one hand, checked before the shear.

Sometimes a section is being reworked and its author wants
the rest of the room to keep out of exactly those
paragraphs while editing freely everywhere else, and a
range lock is that reservation, pinned to the first and
last strand so it covers the same text as the section
moves and grows. A lock is advisory in the honest sense:
it does not make the CRDT refuse operations, because the
CRDT converges regardless, but it lets a well-behaved
client check before minting and warn its user, which is
the layer where social rules belong. The checker answers
whether a proposed edit at a strand falls inside any lock
held by someone else, naming the holder so the request to
coordinate reaches the right person. Locks stack, a strand
can sit under two, and check reports every conflicting
holder rather than the first, because knowing one of two
people to ask is a recipe for asking the wrong one. A lock
whose endpoints are both sheared has lost the text it
guarded and lapses, reported as expired rather than
enforced over a grave, since guarding deleted text is
guarding nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.ids import OpId, check_site
from loom.weave import Weave


@dataclass(frozen=True)
class RangeLock:
    holder: str
    first: OpId
    last: OpId


@dataclass
class Reservations:
    weave: Weave
    locks: list[RangeLock] = field(default_factory=list)

    def reserve(
        self, holder: str, first: OpId, last: OpId
    ) -> str:
        check_site(holder)
        self.locks.append(
            RangeLock(
                holder=holder, first=first, last=last
            )
        )
        return f"{holder} reserved a range"

    def _bounds(self, lock: RangeLock):
        first = self.weave.by_id.get(lock.first)
        last = self.weave.by_id.get(lock.last)
        if first is None or last is None:
            return None
        first_dead = self.weave.strands[first].sheared
        last_dead = self.weave.strands[last].sheared
        if first_dead and last_dead:
            return None
        return first, last

    def holders_at(
        self, strand_id: OpId, mover: str
    ) -> list[str]:
        target = self.weave.by_id.get(strand_id)
        if target is None:
            return []
        found = []
        for lock in self.locks:
            if lock.holder == mover:
                continue
            bounds = self._bounds(lock)
            if bounds is None:
                continue
            first, last = bounds
            if first <= target <= last:
                found.append(lock.holder)
        return sorted(set(found))

    def check(
        self, mover: str, strand_id: OpId
    ) -> str:
        holders = self.holders_at(strand_id, mover)
        if not holders:
            return (
                f"{mover} may edit here; no other "
                "hand has reserved it"
            )
        return (
            f"{mover} should coordinate with "
            + ", ".join(holders)
            + "; this stretch is reserved, and the "
            "lock names whom to ask"
        )

    def expired(self) -> list[RangeLock]:
        return [
            lock
            for lock in self.locks
            if self._bounds(lock) is None
        ]

    def report(self) -> str:
        live = [
            lock
            for lock in self.locks
            if self._bounds(lock) is not None
        ]
        gone = self.expired()
        lines = [
            f"{len(live)} live reservation(s), "
            f"{len(gone)} expired over graves"
        ]
        for lock in live:
            lines.append(f"  held by {lock.holder}")
        return "\n".join(lines)
