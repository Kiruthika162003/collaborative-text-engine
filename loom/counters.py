"""Counters: tallies many hands increment at once, converging without a lock.

A collaborative document counts things, reactions on a
comment, votes on a suggestion, and a naive shared integer
loses increments the instant two hands add at once. The
grow-only counter fixes this the CRDT way: each site keeps
its own subtotal, the value is the sum, and merging takes
the per-site maximum, so an increment lost on the wire is
recovered by the next merge and an increment applied twice
is idempotent because a maximum absorbs repeats. The
plus-minus counter is two grow-only counters, one up and
one down, the value their difference, which is the only
honest way to support decrement, since a single counter
that goes both ways cannot tell a merge whether forty is a
late increment or a healed decrement. Decrement below zero
is allowed, not clamped, because a reaction count that
refuses to go negative is hiding a bug in whoever is
double-removing, and the counter's job is to add up what
happened, not to editorialize it. Merges are commutative
and idempotent, tested by reconciling in both orders and
twice, since those are the two properties every CRDT
claims and few are made to prove.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.ids import check_site


@dataclass
class GrowOnly:
    counts: dict[str, int] = field(default_factory=dict)

    def increment(self, site: str, by: int = 1) -> None:
        check_site(site)
        if by < 0:
            raise ValueError(
                "a grow-only counter only grows"
            )
        self.counts[site] = self.counts.get(site, 0) + by

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: GrowOnly) -> None:
        for site, count in other.counts.items():
            self.counts[site] = max(
                self.counts.get(site, 0), count
            )

    def copy(self) -> GrowOnly:
        return GrowOnly(counts=dict(self.counts))


@dataclass
class PlusMinus:
    ups: GrowOnly = field(default_factory=GrowOnly)
    downs: GrowOnly = field(default_factory=GrowOnly)

    def increment(self, site: str, by: int = 1) -> None:
        self.ups.increment(site, by)

    def decrement(self, site: str, by: int = 1) -> None:
        self.downs.increment(site, by)

    def value(self) -> int:
        return self.ups.value() - self.downs.value()

    def merge(self, other: PlusMinus) -> None:
        self.ups.merge(other.ups)
        self.downs.merge(other.downs)

    def copy(self) -> PlusMinus:
        return PlusMinus(
            ups=self.ups.copy(),
            downs=self.downs.copy(),
        )
