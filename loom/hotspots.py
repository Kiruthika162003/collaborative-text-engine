"""Hotspots: the places two hands wove at once, read from the origins they shared.

A sequence CRDT records, in each strand's origin, the exact
point it was typed after, and when two authors type at the
same point at the same time their strands share an origin and
become siblings the integration has to order. Those shared
origins are the fingerprints of concurrent editing, and this
reads them back: an origin holding strands from more than one
site is a place two hands met, a hotspot, and the count of
its siblings and the sites involved say how crowded it got.
The distinction that keeps it honest is between a run and a
contest. One author typing a word leaves a chain of strands
each originating on the last, not a pile sharing one origin,
so a solo run is not a hotspot no matter how long; only
strands from different sites at one origin count, because the
question is where people collided, not where anyone was busy.
Tombstoned strands are kept in the reckoning, because a spot
where two authors fought and one edit was later deleted was
still a hotspot, and hiding it would erase the history of the
disagreement the tool exists to surface. This measures where
concurrency happened, not whether it caused trouble, in the
reading-organ tradition the whole codebase keeps: the weave
resolved every one of these into a single convergent order,
and a hotspot is a record of collaboration, not a bug report.
"""

from __future__ import annotations

from dataclasses import dataclass

from loom.ids import OpId
from loom.weave import Weave


@dataclass(frozen=True)
class Hotspot:
    origin: OpId | None
    sites: tuple[str, ...]
    siblings: int


def hotspots(weave: Weave) -> list[Hotspot]:
    by_origin: dict[OpId | None, list[str]] = {}
    for strand in weave.strands:
        by_origin.setdefault(strand.origin, []).append(strand.id.site)
    spots = []
    for origin, sites in by_origin.items():
        distinct = sorted(set(sites))
        if len(distinct) > 1:
            spots.append(
                Hotspot(
                    origin=origin,
                    sites=tuple(distinct),
                    siblings=len(sites),
                )
            )
    return sorted(spots, key=lambda spot: (-spot.siblings, spot.sites))


def contested_count(weave: Weave) -> int:
    return len(hotspots(weave))


def sites_in_contention(weave: Weave) -> set[str]:
    involved: set[str] = set()
    for spot in hotspots(weave):
        involved.update(spot.sites)
    return involved


def report(weave: Weave) -> str:
    spots = hotspots(weave)
    if not spots:
        return "no hotspots; no two hands wove at the same point"
    lines = [f"{len(spots)} hotspot(s) where hands met:"]
    for spot in spots:
        where = spot.origin.wire() if spot.origin is not None else "the head"
        lines.append(
            f"  at {where}: {spot.siblings} siblings from "
            + ", ".join(spot.sites)
        )
    lines.append(
        "concurrency, not trouble; the weave resolved every one"
    )
    return "\n".join(lines)
