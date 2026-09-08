"""Redlines: the fabric shown against a baseline, every change wearing a hand.

Tracked changes are a rendering, not a data structure, and
the loom already keeps everything a redline needs: the
baseline says which strands existed then, the fabric says
which stand or lie dead now, and the difference dresses
itself. Additions since the baseline read inline as
bracketed runs with the adding hand named, deletions of
baseline text read as struck runs, and unchanged cloth
reads plain, which is the whole grammar. One species of
change is counted but never shown inline: the glyphs that
were typed and erased both since the baseline, churn that
no reviewer needs woven through the prose but every
reviewer deserves totaled, because a redline that hides
the churn entirely reports the destination while
pretending there was no journey. The counts close the
page, additions and deletions by hand, since review is
negotiation and negotiators like to know who moved what.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class RedlinePiece:
    kind: str
    text: str
    hand: str


def pieces(
    weave: Weave, baseline_ids: set[OpId]
) -> tuple[list[RedlinePiece], int]:
    found: list[RedlinePiece] = []
    silent_churn = 0
    for strand in weave.strands:
        in_baseline = strand.id in baseline_ids
        if strand.sheared and not in_baseline:
            silent_churn += 1
            continue
        if strand.sheared:
            kind = "struck"
        elif in_baseline:
            kind = "plain"
        else:
            kind = "added"
        hand = strand.id.site
        if (
            found
            and found[-1].kind == kind
            and (
                kind == "plain"
                or found[-1].hand == hand
            )
        ):
            found[-1] = RedlinePiece(
                kind=kind,
                text=found[-1].text + strand.glyph,
                hand=found[-1].hand,
            )
        else:
            found.append(
                RedlinePiece(
                    kind=kind,
                    text=strand.glyph,
                    hand=hand,
                )
            )
    return found, silent_churn


def render(
    weave: Weave, baseline: Weave
) -> str:
    baseline_ids = set(baseline.by_id)
    runs, silent_churn = pieces(weave, baseline_ids)
    parts = []
    added_by: dict[str, int] = {}
    struck_by: dict[str, int] = {}
    for piece in runs:
        if piece.kind == "plain":
            parts.append(piece.text)
        elif piece.kind == "added":
            parts.append(
                f"[+{piece.text}+ {piece.hand}]"
            )
            added_by[piece.hand] = added_by.get(
                piece.hand, 0
            ) + len(piece.text)
        else:
            parts.append(f"[-{piece.text}-]")
            struck_by[piece.hand] = struck_by.get(
                piece.hand, 0
            ) + len(piece.text)
    lines = ["".join(parts)]
    for hand in sorted(added_by):
        lines.append(
            f"  {hand} added {added_by[hand]} glyph(s)"
        )
    for hand in sorted(struck_by):
        lines.append(
            f"  {hand}'s baseline text lost "
            f"{struck_by[hand]} glyph(s)"
        )
    if silent_churn:
        lines.append(
            f"  {silent_churn} glyph(s) of silent "
            "churn, typed and erased since the "
            "baseline; the journey, totaled"
        )
    if len(lines) == 1:
        lines.append(
            "  no changes; the baseline is the fabric"
        )
    return "\n".join(lines)
