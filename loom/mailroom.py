"""The mailroom: arrivals sorted into now and not-yet, nothing dropped.

Networks reorder, duplicate, and delay, and the mailroom is
where those habits stop mattering. An arrival is ready when
its site's clock shows the immediately previous counter and
everything it references, an origin to weave after, a
target to shear, is already in the fabric; a ready arrival
is woven and observed, and anything else waits on the
not-yet shelf with a reason attached. Every successful
weave then sweeps the shelf, because one arrival is often
the cork holding back a bottle of others, and the sweep
repeats until a full pass moves nothing. Duplicates are
recognized by the clock and returned as already-woven
receipts rather than errors, the mailroom holding the
strong opinion that a network which repeats itself is
being a network, not being wrong. The shelf is inspectable
and its reasons are sentences, since a silent buffer and a
black hole tell the same story from outside.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.author import Author
from loom.weave import Insert, Op, Shear


@dataclass
class Mailroom:
    author: Author
    shelf: list[Op] = field(default_factory=list)
    woven: int = 0
    duplicates: int = 0

    def _reason_not_ready(self, op: Op) -> str | None:
        expected = self.author.clock.top(op.id.site) + 1
        if op.id.counter > expected:
            return (
                f"waiting for {op.id.site}:"
                f"{expected} to arrive first"
            )
        if isinstance(op, Insert):
            if (
                op.origin is not None
                and op.origin
                not in self.author.weave.by_id
            ):
                return (
                    f"waiting for origin "
                    f"{op.origin.wire()}"
                )
            return None
        if isinstance(op, Shear) and (
            op.target not in self.author.weave.by_id
        ):
            return (
                f"waiting for target "
                f"{op.target.wire()}"
            )
        return None

    def _weave_ready(self, op: Op) -> str:
        receipt = self.author.absorb(op)
        self.woven += 1
        return receipt

    def receive(self, op: Op) -> str:
        if self.author.clock.has(op.id):
            self.duplicates += 1
            return (
                f"{op.id.wire()} is a repeat; a "
                "network which repeats itself is "
                "being a network, not being wrong"
            )
        reason = self._reason_not_ready(op)
        if reason is not None:
            self.shelf.append(op)
            return (
                f"{op.id.wire()} shelved: {reason}"
            )
        receipt = self._weave_ready(op)
        drained = self._sweep()
        if drained:
            receipt += (
                f"; the sweep drained {drained} "
                "shelved arrival(s), one cork often "
                "holding back a bottle"
            )
        return receipt

    def _sweep(self) -> int:
        drained = 0
        moved = True
        while moved:
            moved = False
            for op in list(self.shelf):
                if self.author.clock.has(op.id):
                    self.shelf.remove(op)
                    self.duplicates += 1
                    moved = True
                    continue
                if self._reason_not_ready(op) is None:
                    self.shelf.remove(op)
                    self._weave_ready(op)
                    drained += 1
                    moved = True
        return drained

    def shelf_report(self) -> str:
        if not self.shelf:
            return (
                "the not-yet shelf is empty; every "
                "arrival found its moment"
            )
        lines = [
            f"{len(self.shelf)} arrival(s) on the "
            "not-yet shelf:"
        ]
        for op in self.shelf:
            reason = self._reason_not_ready(op)
            lines.append(
                f"  {op.id.wire()}: {reason}"
            )
        return "\n".join(lines)

    def ledger(self) -> str:
        return (
            f"{self.woven} woven, "
            f"{self.duplicates} repeat(s), "
            f"{len(self.shelf)} still waiting"
        )
