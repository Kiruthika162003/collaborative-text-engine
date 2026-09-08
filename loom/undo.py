"""Undo: unsaying as new operations, never as history rewritten.

Undo in a shared document has one honest shape: minting
new operations that counter the old ones, because pulling
operations back out of a distributed past is a lie the
network will not cosign. The scribe records each local
gesture, and undoing a typing gesture shears the very
strands it wove, while undoing an erasure resurrects each
glyph as a fresh strand anchored on its own tombstone, the
dead strand marking the place the way a headstone marks a
grave, so the text returns where it was even when the
neighborhood has changed around it. Two principles are
enforced by construction rather than permission checks: a
hand may only unsay what it said, the stack holding only
its own gestures, and unsaying is itself sayable, an undo
being ordinary operations any replica weaves without
knowing they are an apology. Redo is the undo of the undo
with fresh identities, and a new gesture burns the redo
pile, since a future edited by hand is no longer the
future anyone stepped back from.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.author import Author
from loom.errors import Invalid
from loom.weave import Insert, Op, Shear


@dataclass
class Scribe:
    author: Author
    said: list[list[Op]] = field(default_factory=list)
    unsaid: list[list[Op]] = field(default_factory=list)

    def type_at(
        self, index: int, text: str
    ) -> list[Op]:
        ops = self.author.type_at(index, text)
        self.said.append(ops)
        self.unsaid.clear()
        return ops

    def erase_at(
        self, index: int, count: int
    ) -> list[Op]:
        ops = self.author.erase_at(index, count)
        self.said.append(ops)
        self.unsaid.clear()
        return ops

    def _counter(self, gesture: list[Op]) -> list[Op]:
        minted: list[Op] = []
        for op in gesture:
            if isinstance(op, Insert):
                shear = Shear(
                    id=self.author._mint(),
                    target=op.id,
                )
                self.author._record(shear)
                minted.append(shear)
            else:
                grave = self.author.weave.strands[
                    self.author.weave.by_id[op.target]
                ]
                self.author.witness_rank += 1
                revival = Insert(
                    id=self.author._mint(),
                    origin=op.target,
                    glyph=grave.glyph,
                    rank=self.author.witness_rank,
                )
                self.author._record(revival)
                minted.append(revival)
        return minted

    def undo(self) -> list[Op]:
        if not self.said:
            raise Invalid(
                "nothing left to take back; a hand "
                "may only unsay what it said"
            )
        gesture = self.said.pop()
        counter = self._counter(gesture)
        self.unsaid.append(counter)
        return counter

    def redo(self) -> list[Op]:
        if not self.unsaid:
            raise Invalid(
                "nothing was unsaid; redo follows "
                "undo the way echo follows voice"
            )
        counter = self.unsaid.pop()
        again = self._counter(counter)
        self.said.append(again)
        return again

    def history_page(self) -> str:
        return (
            f"{len(self.said)} gesture(s) standing, "
            f"{len(self.unsaid)} unsaid and "
            "redoable; a new gesture burns the redo "
            "pile"
        )
