"""Run-length view: contiguous strands from one hand folded into blocks.

An RGA fabric where one person typed a paragraph is a
hundred strands whose ids differ only in their counters,
consecutive and same-sited, which is a compression
opportunity the storage layer leaves on the table. This
module folds runs of strands that share a site and carry
consecutive counters and unbroken origin chains into
single blocks, a lossless summary: the block records the
site, the first counter, the length, and the glyphs, and
the count of blocks against the count of strands is the
compression ratio a real store would see. The fold is a
view and never a mutation, because compressing the
authoritative fabric would break the addressing everything
else depends on, and a summary that alters what it
summarizes is not a summary. Runs break exactly where
convergence cares, at a change of site, a gap in counters,
or a shear, so the block boundaries carry information
rather than hiding it, and a fabric of all singletons folds
to itself, honestly reporting a ratio of one when there is
nothing to gain.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.weave import Weave


@dataclass(frozen=True)
class Run:
    site: str
    first_counter: int
    glyphs: str
    sheared: bool

    def length(self) -> int:
        return len(self.glyphs)


def fold(weave: Weave) -> list[Run]:
    runs: list[Run] = []
    prev = None
    for strand in weave.strands:
        contiguous = (
            prev is not None
            and prev.id.site == strand.id.site
            and prev.id.counter + 1
            == strand.id.counter
            and strand.origin == prev.id
            and prev.sheared == strand.sheared
        )
        if contiguous:
            last = runs[-1]
            runs[-1] = Run(
                site=last.site,
                first_counter=last.first_counter,
                glyphs=last.glyphs + strand.glyph,
                sheared=last.sheared,
            )
        else:
            runs.append(
                Run(
                    site=strand.id.site,
                    first_counter=strand.id.counter,
                    glyphs=strand.glyph,
                    sheared=strand.sheared,
                )
            )
        prev = strand
    return runs


def compression_ratio(weave: Weave) -> float:
    strands = len(weave.strands)
    if strands == 0:
        return 1.0
    return round(strands / len(fold(weave)), 3)


def report(weave: Weave) -> str:
    runs = fold(weave)
    strands = len(weave.strands)
    if strands == 0:
        return "an empty fabric folds to nothing"
    live = sum(1 for run in runs if not run.sheared)
    return (
        f"{strands} strand(s) fold to {len(runs)} "
        f"run(s) ({live} live), ratio "
        f"{compression_ratio(weave)}; runs break "
        "where convergence cares"
    )
