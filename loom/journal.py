"""The journal: every operation kept, because sync is a memory business.

Convergence needs only the fabric, but synchronization
needs the past itself: when a peer says here is my clock,
the only useful answer is the operations that clock has
not covered, and answering requires having kept them. The
journal keeps every operation this station has minted or
heard, keyed by id, recording idempotently since the same
operation arrives as many times as networks please. The
one query that matters, missing_for, returns everything a
given clock lacks, ordered by counter then site, the same
order ids sort in, which keeps each site's operations in
causal order on the wire and leaves the rest to the
receiving mailroom's shelf. The journal never prunes
itself; forgetting is a decision with a safety argument,
the gravedigger's kind of decision, and a journal that
quietly forgets is a sync partner that quietly lies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.clock import VersionVector
from loom.weave import Op


@dataclass
class Journal:
    entries: dict = field(default_factory=dict)

    def record(self, op: Op) -> str:
        if op.id in self.entries:
            return (
                f"{op.id.wire()} already journaled; "
                "memory holds one copy"
            )
        self.entries[op.id] = op
        return f"{op.id.wire()} journaled"

    def missing_for(
        self, clock: VersionVector
    ) -> list[Op]:
        lacking = [
            op
            for op_id, op in self.entries.items()
            if not clock.has(op_id)
        ]
        lacking.sort(
            key=lambda op: (
                op.id.counter,
                op.id.site,
            )
        )
        return lacking

    def size(self) -> int:
        return len(self.entries)
