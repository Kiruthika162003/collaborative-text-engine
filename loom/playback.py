"""Playback: a tape replayed step by step, the document unfolding one gesture at a time.

A tape proves the fabric; playback lets a human watch it
happen, stepping through the recorded operations and asking
the document to render itself at any point along the way.
The stepper holds a cursor into the reel and rebuilds the
fabric up to that cursor on demand, so scrubbing backward
is as cheap as scrubbing forward, no undo stack required,
because the tape is the source of truth and the fabric is
just a view computed from a prefix of it. Each step reports
the operation it just applied in human terms, an insert
naming its glyph and an erasure naming what it struck, so a
reviewer watching the playback reads a narration rather
than a hex dump. Seeking past either end clamps and says
so rather than throwing, because a scrubber that crashes at
the edges is a scrubber nobody scrubs, and the whole point
of playback is that it is safe to poke.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.transcript import Tape
from loom.weave import Insert, Weave


@dataclass
class Playback:
    tape: Tape
    cursor: int = 0

    def _fabric_to(self, cursor: int) -> Weave:
        fabric = Weave()
        for op in self.tape.reel[:cursor]:
            fabric.apply(op)
        return fabric

    def text_now(self) -> str:
        return self._fabric_to(self.cursor).text()

    def step(self) -> str:
        if self.cursor >= self.tape.length():
            return (
                "at the end of the tape; nothing "
                "left to play"
            )
        op = self.tape.reel[self.cursor]
        self.cursor += 1
        if isinstance(op, Insert):
            return (
                f"step {self.cursor}: "
                f"{op.id.site} typed {op.glyph!r}"
            )
        return (
            f"step {self.cursor}: {op.id.site} struck "
            f"{op.target.wire()}"
        )

    def back(self) -> str:
        if self.cursor <= 0:
            return (
                "at the start of the tape; nothing "
                "behind to rewind to"
            )
        self.cursor -= 1
        return (
            f"rewound to step {self.cursor} of "
            f"{self.tape.length()}"
        )

    def seek(self, cursor: int) -> str:
        clamped = max(
            0, min(cursor, self.tape.length())
        )
        note = (
            ""
            if clamped == cursor
            else "; clamped to the tape's edge"
        )
        self.cursor = clamped
        return (
            f"at step {self.cursor} of "
            f"{self.tape.length()}{note}"
        )

    def progress(self) -> str:
        total = self.tape.length()
        percent = (
            self.cursor * 100 // total if total else 100
        )
        return (
            f"step {self.cursor} of {total} "
            f"({percent}%)"
        )
