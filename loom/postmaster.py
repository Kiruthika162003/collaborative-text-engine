"""The postmaster: one wire for the whole document, every kind routed.

The text has a mailroom, but a living document also ships
marks, unmarks, and binder writes, and the postmaster is
the sorting office that gives them all one wire. Text
operations ride the standard encoding untouched and route
to the station, whose mailroom already knows how to wait.
Attire gets the same courtesy the mailroom shows strands:
a mark naming strands that have not arrived is shelved
with its reason, and every successful delivery sweeps the
attire shelf, one cork holding back a bottle here exactly
as it does downstairs. Binder writes route to their
registers, which are commutative and need no shelf at
all, arriving in any order and settling the same. The
envelope verbs are a closed set and torn envelopes are
refused with the line quoted, because a sorting office
that guesses at addresses delivers everything eventually,
each to the wrong room.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loom.binder import Binder
from loom.errors import Missing, Torn
from loom.ids import OpId
from loom.marks import Mark, Unmark, Wardrobe
from loom.registers import Write
from loom.station import Station
from loom.wire import (
    decode,
    encode,
    escape_glyph,
    unescape_glyph,
)

Attire = Mark | Unmark


def encode_mark(mark: Mark) -> str:
    return (
        f"mrk|{mark.id.wire()}|{mark.style}|"
        f"{mark.start.wire()}|{mark.end.wire()}"
    )


def encode_unmark(unmark: Unmark) -> str:
    return (
        f"unm|{unmark.id.wire()}|"
        f"{unmark.mark_id.wire()}"
    )


def encode_binder_write(
    kind: str, entry: Write
) -> str:
    if kind not in ("ttl", "sts"):
        raise Torn(
            f"{kind!r} is not a binder verb; the "
            "binder speaks ttl and sts"
        )
    return (
        f"{kind}|{entry.site}|{entry.rank}|"
        f"{escape_glyph(entry.value)}"
    )


@dataclass
class Postmaster:
    station: Station
    wardrobe: Wardrobe
    binder: Binder
    attire_shelf: list[Attire] = field(
        default_factory=list
    )
    routed: dict[str, int] = field(default_factory=dict)

    def _bump(self, kind: str) -> None:
        self.routed[kind] = (
            self.routed.get(kind, 0) + 1
        )

    def _try_attire(self, item: Attire) -> str | None:
        try:
            if isinstance(item, Mark):
                return self.wardrobe.dress(item)
            return self.wardrobe.strip(item)
        except Missing:
            return None

    def _sweep_attire(self) -> int:
        drained = 0
        moved = True
        while moved:
            moved = False
            for item in list(self.attire_shelf):
                receipt = self._try_attire(item)
                if receipt is not None:
                    self.attire_shelf.remove(item)
                    drained += 1
                    moved = True
        return drained

    def dispatch(self, line: str) -> str:
        verb = line.split("|", 1)[0]
        if verb in ("ins", "shr"):
            receipt = self.station.hear(decode(line))
            self._bump("text")
            drained = self._sweep_attire()
            if drained:
                receipt += (
                    f"; {drained} attire item(s) "
                    "drained off the shelf"
                )
            return receipt
        parts = line.split("|")
        if verb == "mrk":
            if len(parts) != 5:
                raise Torn(
                    f"{line!r} is not a mark envelope"
                )
            mark = Mark(
                id=OpId.parse(parts[1]),
                style=parts[2],
                start=OpId.parse(parts[3]),
                end=OpId.parse(parts[4]),
            )
            self._bump("attire")
            receipt = self._try_attire(mark)
            if receipt is None:
                self.attire_shelf.append(mark)
                return (
                    f"{mark.id.wire()} shelved: its "
                    "pins have not arrived"
                )
            return receipt
        if verb == "unm":
            if len(parts) != 3:
                raise Torn(
                    f"{line!r} is not an unmark "
                    "envelope"
                )
            unmark = Unmark(
                id=OpId.parse(parts[1]),
                mark_id=OpId.parse(parts[2]),
            )
            self._bump("attire")
            receipt = self._try_attire(unmark)
            if receipt is None:
                self.attire_shelf.append(unmark)
                return (
                    f"{unmark.id.wire()} shelved: "
                    "its mark has not arrived"
                )
            return receipt
        if verb in ("ttl", "sts"):
            if len(parts) != 4:
                raise Torn(
                    f"{line!r} is not a binder "
                    "envelope"
                )
            entry = Write(
                site=parts[1],
                rank=int(parts[2]),
                value=unescape_glyph(parts[3]),
            )
            self._bump("binder")
            if verb == "ttl":
                return self.binder.retitle(entry)
            return self.binder.declare(entry)
        raise Torn(
            f"{line!r} opens with {verb!r}; the "
            "sorting office guesses at no addresses"
        )

    def post_text(self, ops) -> list[str]:
        return [self.dispatch(encode(op)) for op in ops]

    def ledger(self) -> str:
        counts = ", ".join(
            f"{kind}: {self.routed[kind]}"
            for kind in sorted(self.routed)
        )
        return (
            f"routed {counts or 'nothing'}; "
            f"{len(self.attire_shelf)} attire "
            "item(s) waiting"
        )
