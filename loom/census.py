"""The census: the fabric's structure counted, history worn openly.

Attribution answers who; the census answers what shape,
the numbers an operator reads before deciding anything:
how many strands the fabric carries against how many still
show, the dead ratio that says when the gravedigger earns
a visit, the number of hands that ever touched the cloth,
the high-water rank that says how much witnessing the
newest glyph carries, and the longest unbroken run of one
hand, which measures whether this document was written or
negotiated. The dead ratio is reported in percent with the
threshold stated beside it, a fabric past forty percent
tombstone wearing more history than text, and the page
never prescribes, in the tradition of mirrors: the numbers
are the operator's to act on, and a census that nags is a
census that gets skipped.
"""

from __future__ import annotations

from loom.weave import Weave

HEAVY_HISTORY_PERCENT = 40


def longest_single_hand_run(weave: Weave) -> int:
    longest = 0
    current_site = None
    current_run = 0
    for strand in weave.strands:
        if strand.sheared:
            continue
        if strand.id.site == current_site:
            current_run += 1
        else:
            current_site = strand.id.site
            current_run = 1
        longest = max(longest, current_run)
    return longest


def hands_seen(weave: Weave) -> list[str]:
    return sorted(
        {
            strand.id.site
            for strand in weave.strands
        }
        | {
            shear_id.site
            for shear_id in weave.shears_seen
        }
    )


def high_water_rank(weave: Weave) -> int:
    return max(
        (
            strand.rank
            for strand in weave.strands
        ),
        default=0,
    )


def page(weave: Weave) -> str:
    total = len(weave.strands)
    if total == 0:
        return (
            "an unwoven fabric; every number is zero "
            "and every future is open"
        )
    dead = weave.tombstone_count()
    dead_percent = dead * 100 // total
    lines = [
        f"{total} strand(s), "
        f"{weave.visible_count()} showing, "
        f"{dead} dead ({dead_percent}%)"
    ]
    if dead_percent >= HEAVY_HISTORY_PERCENT:
        lines.append(
            f"  past the {HEAVY_HISTORY_PERCENT}% "
            "line; the fabric wears more history "
            "than text"
        )
    lines.append(
        f"{len(hands_seen(weave))} hand(s) ever "
        "touched the cloth: "
        + ", ".join(hands_seen(weave))
    )
    lines.append(
        f"high-water rank {high_water_rank(weave)}; "
        "how much witnessing the newest glyph carries"
    )
    lines.append(
        f"longest single-hand run "
        f"{longest_single_hand_run(weave)}; whether "
        "this was written or negotiated"
    )
    lines.append(
        "numbers only; a census that nags is a "
        "census that gets skipped"
    )
    return "\n".join(lines)
