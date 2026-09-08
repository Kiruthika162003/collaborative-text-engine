"""The author: one hand at the loom, minting what it types.

An author is the local editing surface: a site name, a
weave, and a clock, translating human gestures, type this
at position four, erase those two glyphs, into operations
the fabric can weave anywhere. Every glyph typed mints the
site's next counter and originates on the glyph to its
left at the moment of typing, which is how a run travels
as a block, and every local operation applies to the
author's own weave immediately, because the person typing
must see their keystroke now and the network can hear
about it whenever the network is ready. Erasure resolves
visible positions to strand ids before minting shears,
positions being a conversation between a human and their
screen while ids are the only language replicas share.
The author keeps two numbers that must never be confused:
the per-site counter, counting its own operations for
delivery, contiguous by law, and the witness rank, a
Lamport stamp grown by everything absorbed from anywhere,
stamped onto inserts so sibling contests are won by
whoever has seen more, not whoever has typed more. The
distinction was paid for in the duet trial, where one
counter doing both jobs produced the foxbrown.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.clock import VersionVector
from loom.errors import Invalid
from loom.ids import OpId
from loom.weave import Insert, Op, Shear, Weave


@dataclass
class Author:
    site: str
    weave: Weave = field(default_factory=Weave)
    clock: VersionVector = field(
        default_factory=VersionVector
    )
    witness_rank: int = 0

    def _mint(self) -> OpId:
        return OpId(
            site=self.site,
            counter=self.clock.top(self.site) + 1,
        )

    def _record(self, op: Op) -> None:
        self.weave.apply(op)
        self.clock.observe(op.id)

    def absorb(self, op: Op) -> str:
        """Weave a remote operation and let the witness rank grow with it."""
        receipt = self.weave.apply(op)
        self.clock.observe(op.id)
        if isinstance(op, Insert):
            self.witness_rank = max(
                self.witness_rank, op.rank
            )
        return receipt

    def type_at(
        self, index: int, text: str
    ) -> list[Op]:
        if not text:
            raise Invalid(
                "typing nothing mints nothing; the "
                "gesture must carry glyphs"
            )
        anchor = self.weave.origin_for_insert_at(index)
        minted: list[Op] = []
        for glyph in text:
            self.witness_rank += 1
            op = Insert(
                id=self._mint(),
                origin=anchor,
                glyph=glyph,
                rank=self.witness_rank,
            )
            self._record(op)
            anchor = op.id
            minted.append(op)
        return minted

    def erase_at(
        self, index: int, count: int
    ) -> list[Op]:
        if count < 1:
            raise Invalid(
                "erasing zero glyphs is a gesture at "
                "nothing"
            )
        targets = [
            self.weave.strand_at_visible(index).id
            for index in range(index, index + count)
        ]
        minted: list[Op] = []
        for target in targets:
            op = Shear(id=self._mint(), target=target)
            self._record(op)
            minted.append(op)
        return minted

    def text(self) -> str:
        return self.weave.text()
