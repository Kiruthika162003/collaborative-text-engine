"""Snapshots: the fabric frozen whole, and two digests with different oaths.

A snapshot writes every strand, tombstones included,
because a snapshot of only the visible text is a
photograph of a building with the foundation cropped out,
loadable but unable to seat late arrivals. The form is a
header carrying the strand count, then one line per strand
in fabric order, and thawing verifies the count and
rebuilds the index rather than trusting the page, since a
snapshot is exactly the kind of file that gets truncated
by full disks and edited by helpful hands. Two digests
serve two oaths. The fabric digest covers everything and
is the convergence oath, two replicas matching here agree
about the past, the dead, and the order of both. The cloth
digest covers only what a reader sees and is the display
oath, cheaper and weaker, and the pair exists because the
strong claim and the cheap claim are both useful and
neither should have to impersonate the other.
"""

from __future__ import annotations

import hashlib

from loom.errors import Torn
from loom.ids import OpId
from loom.weave import HEAD, Strand, Weave
from loom.wire import escape_glyph, unescape_glyph

HEADER = "loomsnap"
HEAD_MARK = "^"


def freeze(weave: Weave) -> str:
    lines = [f"{HEADER}|{len(weave.strands)}"]
    for strand in weave.strands:
        origin = (
            HEAD_MARK
            if strand.origin is HEAD
            else strand.origin.wire()
        )
        flag = "x" if strand.sheared else "."
        lines.append(
            f"{strand.id.wire()}|{origin}|"
            f"{strand.rank}|{flag}|"
            f"{escape_glyph(strand.glyph)}"
        )
    return "\n".join(lines)


def thaw(page: str) -> Weave:
    lines = page.split("\n")
    head, _, count_text = lines[0].partition("|")
    if head != HEADER:
        raise Torn(
            f"{lines[0]!r} is not a snapshot header; "
            "snapshots open with the word loomsnap"
        )
    try:
        count = int(count_text)
    except ValueError as wrong:
        raise Torn(
            "the header count is not a number"
        ) from wrong
    body = lines[1:]
    if len(body) != count:
        raise Torn(
            f"the header promises {count} strand(s) "
            f"and the page carries {len(body)}; "
            "snapshots are exactly the kind of file "
            "full disks truncate"
        )
    weave = Weave()
    for line in body:
        parts = line.split("|")
        if len(parts) != 5:
            raise Torn(
                f"{line!r} is not a strand line"
            )
        id_text, origin_text, rank_text, flag, glyph = (
            parts
        )
        if flag not in (".", "x"):
            raise Torn(
                f"{line!r} carries flag {flag!r}; a "
                "strand is living or sheared, nothing "
                "third"
            )
        try:
            rank = int(rank_text)
        except ValueError as wrong:
            raise Torn(
                f"{line!r} carries a wordy rank"
            ) from wrong
        weave.strands.append(
            Strand(
                id=OpId.parse(id_text),
                origin=(
                    HEAD
                    if origin_text == HEAD_MARK
                    else OpId.parse(origin_text)
                ),
                glyph=unescape_glyph(glyph),
                rank=rank,
                sheared=flag == "x",
            )
        )
    for index, strand in enumerate(weave.strands):
        if strand.id in weave.by_id:
            raise Torn(
                f"{strand.id.wire()} appears twice; "
                "one id, one strand, no exceptions"
            )
        weave.by_id[strand.id] = index
    return weave


def fabric_digest(weave: Weave) -> str:
    return hashlib.sha256(
        freeze(weave).encode()
    ).hexdigest()[:16]


def cloth_digest(weave: Weave) -> str:
    return hashlib.sha256(
        weave.text().encode()
    ).hexdigest()[:16]


def same_fabric(one: Weave, two: Weave) -> bool:
    return fabric_digest(one) == fabric_digest(two)
