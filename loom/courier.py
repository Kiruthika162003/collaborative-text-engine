"""The courier: a network that misbehaves on schedule, so trials can too.

Real networks reorder and repeat whenever they please;
this one does it deterministically, because a trial that
fails under mischief must fail the same way tomorrow or
the failure teaches nothing. A link carries operations one
way between two sites under a temperament: calm delivers
in order, tides shuffles each batch, and gremlin shuffles
and also duplicates a deterministic portion, every choice
drawn from a seeded generator so the chaos is a fixture,
not a mood. Links never drop, and that is a documented
boundary rather than an oversight: loss is the business of
the handshake and its retransmissions, while the courier's
business is proving the weave indifferent to order and
repetition, and a boundary two modules both think is
theirs is how systems drop things politely. The ledger
counts posted, delivered, and duplicated, so a trial can
bill the mischief precisely.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from loom.errors import Invalid
from loom.mailroom import Mailroom
from loom.weave import Op

TEMPERAMENTS = ("calm", "tides", "gremlin")
GREMLIN_DUPLICATE_EVERY = 3


@dataclass
class Link:
    to: Mailroom
    temperament: str = "calm"
    seed: int = 0
    pending: list[Op] = field(default_factory=list)
    posted: int = 0
    delivered: int = 0
    duplicated: int = 0

    def __post_init__(self) -> None:
        if self.temperament not in TEMPERAMENTS:
            raise Invalid(
                f"{self.temperament!r} is not a "
                "temperament; the courier knows "
                + ", ".join(TEMPERAMENTS)
            )
        self._dice = random.Random(self.seed)

    def post(self, op: Op) -> None:
        self.pending.append(op)
        self.posted += 1

    def post_many(self, ops: list[Op]) -> None:
        for op in ops:
            self.post(op)

    def deliver_batch(self) -> int:
        if not self.pending:
            return 0
        batch = list(self.pending)
        self.pending.clear()
        if self.temperament in ("tides", "gremlin"):
            self._dice.shuffle(batch)
        if self.temperament == "gremlin":
            repeats = [
                op
                for index, op in enumerate(batch)
                if index % GREMLIN_DUPLICATE_EVERY == 0
            ]
            for op in repeats:
                batch.insert(
                    self._dice.randrange(
                        len(batch) + 1
                    ),
                    op,
                )
                self.duplicated += 1
        for op in batch:
            self.to.receive(op)
            self.delivered += 1
        return len(batch)

    def ledger(self) -> str:
        return (
            f"{self.posted} posted, "
            f"{self.delivered} delivered, "
            f"{self.duplicated} duplicated, "
            f"{len(self.pending)} in flight"
        )
