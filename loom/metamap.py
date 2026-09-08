"""The metamap: arbitrary key-value document metadata, last writer winning per key.

Beyond title and status a document accumulates loose
metadata, a due date, a color, a folder, and the metamap
holds those as a last-writer-wins map where each key
settles independently. A write carries a key, a value, and
the witness rank of the hand that made it, and the winner
for a key is the highest rank with the site name breaking
ties, the same total order the weave itself trusts, so two
replicas shown the same writes agree on every key without
a conversation. Deletion is a write of a tombstone value
rather than a removal, because a key that vanishes from the
map cannot outvote a concurrent write that set it, and a
delete that loses to a later set is exactly what should
happen, the set being newer. Reading a tombstoned key
reports it absent while the tombstone stays to arbitrate,
and the merge takes the winning write per key from either
side, commutative and idempotent, proven by reconciling
both orders twice, because a metadata map that disagrees
across replicas is a document that cannot agree on its own
name.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TOMBSTONE = object()


@dataclass(frozen=True)
class Write:
    key: str
    value: object
    rank: int
    site: str

    def seat_key(self) -> tuple[int, str]:
        return (self.rank, self.site)


@dataclass
class MetaMap:
    winners: dict = field(default_factory=dict)

    def _apply(self, write: Write) -> bool:
        held = self.winners.get(write.key)
        if (
            held is None
            or write.seat_key() > held.seat_key()
        ):
            self.winners[write.key] = write
            return True
        return False

    def set(
        self, key: str, value: object, rank: int, site: str
    ) -> str:
        write = Write(
            key=key, value=value, rank=rank, site=site
        )
        won = self._apply(write)
        return (
            f"{key} set to {value!r}"
            if won
            else f"{key} write yielded to a later one"
        )

    def delete(
        self, key: str, rank: int, site: str
    ) -> str:
        self._apply(
            Write(
                key=key,
                value=TOMBSTONE,
                rank=rank,
                site=site,
            )
        )
        return f"{key} deletion recorded"

    def get(self, key: str, default: object = None):
        held = self.winners.get(key)
        if held is None or held.value is TOMBSTONE:
            return default
        return held.value

    def has(self, key: str) -> bool:
        held = self.winners.get(key)
        return (
            held is not None
            and held.value is not TOMBSTONE
        )

    def keys(self) -> list[str]:
        return sorted(
            key
            for key, write in self.winners.items()
            if write.value is not TOMBSTONE
        )

    def merge(self, other: MetaMap) -> None:
        for write in other.winners.values():
            self._apply(write)

    def copy(self) -> MetaMap:
        clone = MetaMap()
        clone.winners = dict(self.winners)
        return clone
