"""Throttle: a token bucket that paces the wire without ever dropping an op.

Bursty typing floods a network, and a throttle is the fix
that must not become a bug: it may delay operations but
must never drop one, because a dropped operation in a
convergent system is a divergence with a euphemism. This
is a token bucket over a logical clock the caller advances,
tokens refilling at a steady rate up to a cap, each shipped
operation spending one, and when the bucket is empty the
operations wait, they do not vanish. The clock is logical
and injected rather than read from the wall, because a
throttle that reads the real clock cannot be tested and a
convergence primitive that cannot be tested is a rumor.
The bucket caps its own fill so a long-idle sender cannot
save up an unlimited burst, since the point of the throttle
is smoothing and a saved-up flood is the opposite of
smooth. The report states tokens available and operations
waiting, the two numbers an operator needs to know whether
the wire or the bucket is the bottleneck.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.errors import Invalid
from loom.weave import Op


@dataclass
class TokenBucket:
    rate: float
    cap: float
    tokens: float = 0.0
    last_tick: int = 0
    waiting: list[Op] = field(default_factory=list)
    shipped: int = 0

    def __post_init__(self) -> None:
        if self.rate <= 0 or self.cap <= 0:
            raise Invalid(
                "a bucket with no rate or no cap "
                "paces nothing"
            )
        self.tokens = self.cap

    def advance(self, tick: int) -> None:
        if tick < self.last_tick:
            raise Invalid(
                "the logical clock ran backward; a "
                "throttle over a rewinding clock is "
                "nonsense"
            )
        elapsed = tick - self.last_tick
        self.last_tick = tick
        self.tokens = min(
            self.cap, self.tokens + elapsed * self.rate
        )

    def offer(self, op: Op) -> None:
        self.waiting.append(op)

    def offer_many(self, ops: list[Op]) -> None:
        self.waiting.extend(ops)

    def drain(self) -> list[Op]:
        shipped: list[Op] = []
        while self.waiting and self.tokens >= 1:
            shipped.append(self.waiting.pop(0))
            self.tokens -= 1
        self.shipped += len(shipped)
        return shipped

    def report(self) -> str:
        return (
            f"{self.tokens:.1f} token(s) available, "
            f"{len(self.waiting)} op(s) waiting, "
            f"{self.shipped} shipped; delayed never "
            "dropped"
        )
