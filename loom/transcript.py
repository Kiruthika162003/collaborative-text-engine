"""The tape: everything woven, in the order it wove, replayable to the digest.

The journal remembers what exists; the tape remembers what
happened, every operation in the exact order this station
wove it, and the difference is the difference between a
warehouse and a security recording. Replay builds a fresh
fabric by applying the tape front to back, and because the
tape records weave order, never arrival order, the replay
needs no mailroom, no shelf, and no forgiveness, each
operation finding its origin already present or the tape
convicting itself on the spot: a tape is an order, not a
bag, and a shuffled tape refuses to play. The proof this
module exists for is digest equality, the replayed fabric
matching the living one to the byte, which turns the tape
into the audit nobody can argue with, and the dump rides
the standard wire so a tape can leave the building and
still testify.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.snapshot import fabric_digest
from loom.weave import Op, Weave
from loom.wire import decode_many, encode_many


@dataclass
class Tape:
    reel: list[Op] = field(default_factory=list)

    def record(self, op: Op) -> None:
        self.reel.append(op)

    def replay(self) -> Weave:
        fabric = Weave()
        for op in self.reel:
            fabric.apply(op)
        return fabric

    def testifies_for(self, living: Weave) -> bool:
        return fabric_digest(self.replay()) == (
            fabric_digest(living)
        )

    def dump(self) -> str:
        return encode_many(self.reel)

    @classmethod
    def load(cls, page: str) -> Tape:
        return cls(reel=decode_many(page))

    def length(self) -> int:
        return len(self.reel)
