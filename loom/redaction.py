"""Redaction: content scrubbed for good, structure kept so replicas still agree.

Deletion in this engine shears a strand but keeps its glyph
in the tombstone, which is right for undo and wrong for a
leaked password: some removals must destroy the content,
not merely hide it. Redaction threads that needle. It
replaces the glyphs of a stretch with a block character
while leaving the strands, their ids, and their positions
exactly in place, so convergence is untouched, a late
arrival still anchors correctly, and yet the original text
is genuinely gone from the fabric, not recoverable by
reading a tombstone. A redaction is itself an operation
every replica applies, because a redaction that happens on
one machine and not the others is a leak that healed
everywhere except where it mattered. The redacted count is
reported and the block character is uniform, so a reader
sees that something was here and cannot see what, which is
the exact and only thing redaction promises. Redacting an
already-redacted strand is idempotent, since scrubbing
clean bytes changes nothing and must be safe to repeat when
the operation arrives twice.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.errors import Missing
from loom.ids import OpId
from loom.weave import Weave

BLOCK = "█"


@dataclass(frozen=True)
class Redact:
    id: OpId
    targets: tuple[OpId, ...]


@dataclass
class Redactor:
    weave: Weave
    applied: set = None

    def __post_init__(self) -> None:
        if self.applied is None:
            self.applied = set()

    def redact(self, redaction: Redact) -> str:
        if redaction.id in self.applied:
            return (
                f"{redaction.id.wire()} already "
                "applied; scrubbing clean bytes is "
                "idempotent"
            )
        scrubbed = 0
        for target in redaction.targets:
            position = self.weave.by_id.get(target)
            if position is None:
                raise Missing(
                    f"{target.wire()} is not in the "
                    "fabric to redact. Buffer it"
                )
            strand = self.weave.strands[position]
            if strand.glyph != BLOCK:
                self.weave.strands[position] = type(
                    strand
                )(
                    id=strand.id,
                    origin=strand.origin,
                    glyph=BLOCK,
                    rank=strand.rank,
                    sheared=strand.sheared,
                )
                scrubbed += 1
        self.applied.add(redaction.id)
        return (
            f"{scrubbed} glyph(s) scrubbed; the text "
            "is gone, the structure stayed"
        )

    def redacted_count(self) -> int:
        return sum(
            1
            for strand in self.weave.strands
            if strand.glyph == BLOCK
            and not strand.sheared
        )


def redact_range(
    weave: Weave,
    redactor: Redactor,
    redaction_id: OpId,
    start: int,
    count: int,
) -> str:
    targets = tuple(
        weave.strand_at_visible(start + offset).id
        for offset in range(count)
    )
    return redactor.redact(
        Redact(id=redaction_id, targets=targets)
    )
