"""The outbox: local operations held briefly, then shipped as one honest batch.

Shipping every keystroke as its own packet is correct and
wasteful; the outbox holds a hand's operations and releases
them in batches, trading a little latency for a lot of
packets, which is the trade every real editor makes. What
the outbox refuses to do is the tempting optimization that
breaks convergence: it never coalesces an insert and a
later shear of the same strand into nothing, because the
remote replica may have anchored a third party's glyph on
that strand between the two, and a strand that never
existed cannot anchor anyone. So the outbox coalesces only
what is safe, dropping exact duplicate ids, and ships
everything else in mint order, the order that keeps each
site's operations causally sound on the wire. Flushing
empties the box and returns the batch; peeking reads
without emptying; and the high-water mark records the
fullest the box ever got, the number that sizes a real
buffer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.weave import Op


@dataclass
class Outbox:
    pending: list[Op] = field(default_factory=list)
    seen: set = field(default_factory=set)
    shipped: int = 0
    high_water: int = 0

    def hold(self, op: Op) -> str:
        if op.id in self.seen:
            return (
                f"{op.id.wire()} already held; the "
                "box drops exact duplicates and "
                "nothing braver"
            )
        self.seen.add(op.id)
        self.pending.append(op)
        self.high_water = max(
            self.high_water, len(self.pending)
        )
        return f"{op.id.wire()} held; {len(self.pending)} waiting"

    def hold_many(self, ops: list[Op]) -> None:
        for op in ops:
            self.hold(op)

    def peek(self) -> list[Op]:
        return list(self.pending)

    def flush(self) -> list[Op]:
        batch = sorted(
            self.pending,
            key=lambda op: (
                op.id.counter,
                op.id.site,
            ),
        )
        self.shipped += len(batch)
        self.pending.clear()
        return batch

    def is_empty(self) -> bool:
        return not self.pending

    def ledger(self) -> str:
        return (
            f"{len(self.pending)} waiting, "
            f"{self.shipped} shipped, high-water "
            f"{self.high_water}; latency traded for "
            "packets, never for convergence"
        )
