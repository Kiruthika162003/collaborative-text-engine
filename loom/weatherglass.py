"""The weatherglass: the circle's weather read off the instruments it keeps.

Every link already keeps a ledger and every mailroom a
shelf, so the weatherglass invents no sensors, it reads
the ones installed: postings, deliveries, and manufactured
duplicates summed across links, the busiest link named
with its numbers because traffic is never uniform and the
hot pair is where trouble will visit first, the in-flight
count that says how much is currently riding the wires,
and the shelved count that says how much has arrived and
cannot yet be woven. The forecast at the end is a state,
not a scolding: all quiet when nothing rides and nothing
waits, mail in flight when the wires are carrying, and
shelf backlog when arrivals outran their origins, each
with the number attached, because an operator handed a
mood without a measurement has been handed nothing.
"""

from __future__ import annotations

from loom.circle import Circle


def busiest_link(circle: Circle) -> str:
    heaviest = max(
        circle.links.items(),
        key=lambda held: (
            held[1].posted,
            held[0],
        ),
    )
    (source, target), link = heaviest
    return (
        f"{source} -> {target} carried "
        f"{link.posted} posting(s)"
    )


def in_flight(circle: Circle) -> int:
    return sum(
        len(link.pending)
        for link in circle.links.values()
    )


def shelved(circle: Circle) -> int:
    return sum(
        len(room.shelf)
        for room in circle.mailrooms.values()
    )


def forecast(circle: Circle) -> str:
    riding = in_flight(circle)
    waiting = shelved(circle)
    if riding == 0 and waiting == 0:
        return (
            "all quiet; nothing rides, nothing waits"
        )
    if waiting == 0:
        return (
            f"mail in flight: {riding} operation(s) "
            "riding the wires"
        )
    return (
        f"shelf backlog: {waiting} arrival(s) "
        f"waiting on origins, {riding} still riding"
    )


def report(circle: Circle) -> str:
    posted = sum(
        link.posted for link in circle.links.values()
    )
    delivered = sum(
        link.delivered
        for link in circle.links.values()
    )
    duplicated = sum(
        link.duplicated
        for link in circle.links.values()
    )
    temperaments = sorted(
        {
            link.temperament
            for link in circle.links.values()
        }
    )
    lines = [
        f"{len(circle.links)} link(s) under "
        + ", ".join(temperaments)
        + " weather",
        f"  {posted} posted, {delivered} delivered, "
        f"{duplicated} duplicate(s) manufactured",
        f"  busiest: {busiest_link(circle)}",
        f"  in flight {in_flight(circle)}, "
        f"shelved {shelved(circle)}",
        f"forecast: {forecast(circle)}",
        "instruments only; a mood without a "
        "measurement is nothing",
    ]
    return "\n".join(lines)
